/**
 * Session Enforcement Plugin for OpenCode
 *
 * Injects session context into the LLM system prompt and enforces
 * skill invocation rules. Also detects bare issue references (#N)
 * and injects mandatory audit pipelines.
 *
 * Hook: system.transform — pushes English prose context (from session-init
 *   and PluginInput augmentations) into the LLM system prompt.
 * Hook: chat.messages.transform — injects skill enforcement content and
 *   bare issue pipeline directives into user messages.
 *
 * NO shell.env hook — env-loader.ts owns all bash environment injection.
 * NO parsing of session-init output — stdout goes verbatim to system prompt.
 *
 * Source attribution:
 * - Session init pattern adapted from existing session-init.ts (project-internal)
 * - Skill enforcement injection adapted from obra/superpowers
 *   https://github.com/obra/superpowers/blob/main/.opencode/plugins/superpowers.js
 * - Red-flags rationalization table adapted from obra/superpowers writing-skills
 *   https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md
 * - CSO (Content Search Optimization) principles adapted from obra/superpowers
 *   https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md
 *
 * Co-authored with AI: OpenCode (ollama-cloud/glm-5)
 */

import type { Hooks, PluginInput } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";
import { execSync } from "child_process";

const CACHE_TTL_MS = 5 * 60 * 1000;

interface PluginDiagnostic {
  source: string;
  level: "error" | "warning" | "info";
  message: string;
  exitCode?: number;
}

const DIAGNOSTICS_PATH = path.join(".opencode", "tmp", "plugin-diagnostics.jsonl");

function writeDiagnostic(projectDir: string, diagnostic: PluginDiagnostic): void {
  const fullPath = path.join(projectDir, DIAGNOSTICS_PATH);
  const dir = path.dirname(fullPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const line = JSON.stringify(diagnostic) + "\n";
  fs.appendFileSync(fullPath, line, "utf8");
}

function collectDiagnostics(projectDir: string): PluginDiagnostic[] {
  const fullPath = path.join(projectDir, DIAGNOSTICS_PATH);
  if (!fs.existsSync(fullPath)) {
    return [];
  }
  try {
    const content = fs.readFileSync(fullPath, "utf8");
    const diagnostics: PluginDiagnostic[] = [];
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        diagnostics.push(JSON.parse(trimmed));
      } catch {
        // Skip malformed lines
      }
    }
    // Clear the file after reading
    fs.writeFileSync(fullPath, "", "utf8");
    return diagnostics;
  } catch {
    return [];
  }
}

function buildDiagnosticBlock(diagnostics: PluginDiagnostic[]): string {
  if (diagnostics.length === 0) return "";

  const entries = diagnostics.map(d => {
    let line = `- [${d.level.toUpperCase()}] ${d.source}: ${d.message}`;
    if (d.exitCode !== undefined) {
      line += ` (exit code ${d.exitCode})`;
    }
    return line;
  }).join("\n");

  const hasErrors = diagnostics.some(d => d.level.toUpperCase() === "ERROR");

  if (hasErrors) {
    const actions = diagnostics
      .filter(d => d.level.toUpperCase() === "ERROR")
      .map(d => `- Investigate and resolve the ${d.source} ERROR before proceeding`)
      .join("\n");

    return `<PLUGIN_DIAGNOSTICS>
⚠️ The following plugin diagnostics were collected during session startup:

${entries}

🚫 MUST NOT proceed — ERROR-level diagnostics detected. HALT immediately and resolve these errors.

**MANDATORY ACTIONS:**
${actions}

Do NOT continue with any operations until ALL ERROR-level diagnostics are resolved.
</PLUGIN_DIAGNOSTICS>`;
  }

  return `<PLUGIN_DIAGNOSTICS>
⚠️ The following plugin diagnostics were collected during session startup:

${entries}

Review these diagnostics. For errors, investigate the source script. For warnings, assess whether action is needed.
</PLUGIN_DIAGNOSTICS>`;
}

let cachedOutput: string | null = null;
let cacheTimestamp = 0;

/**
 * Process-scoped set of session IDs that are sub-agent sessions
 * (sessions with a parentID). Populated in system.transform by
 * querying client.session.get() for parentID. Used in messages.transform
 * to gate first-turn-only injections for sub-agent sessions.
 *
 * REQ-5: No disk persistence — the set is rebuilt from live API queries
 * on each process restart, never written to disk.
 */
const subAgentSessions = new Set<string>();

function resolveGitDir(projectDir: string): string | null {
  try {
    const result = execSync("git rev-parse --git-dir", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
    if (path.isAbsolute(result)) return result;
    return path.resolve(projectDir, result);
  } catch {
    return null;
  }
}

function ensureHooksInstalled(projectDir: string): void {
  const hooksSourceDir = path.join(projectDir, ".opencode", "hooks");
  if (!fs.existsSync(hooksSourceDir)) {
    console.error("[session-enforcement] .opencode/hooks/ directory missing — repo integrity problem");
    writeDiagnostic(projectDir, {
      source: "session-enforcement",
      level: "error",
      message: ".opencode/hooks/ directory missing — repo integrity problem",
    });
    return;
  }

  const gitDir = resolveGitDir(projectDir);
  if (!gitDir) {
    console.error("[session-enforcement] Could not resolve .git directory for hooks installation");
    writeDiagnostic(projectDir, {
      source: "session-enforcement",
      level: "error",
      message: "Could not resolve .git directory for hooks installation",
    });
    return;
  }

  const hooksTargetDir = path.join(gitDir, "hooks");
  fs.mkdirSync(hooksTargetDir, { recursive: true });

  const sourceEntries = fs.readdirSync(hooksSourceDir);
  for (const hookName of sourceEntries) {
    const sourcePath = path.join(hooksSourceDir, hookName);
    if (!fs.statSync(sourcePath).isFile()) continue;
    if (hookName.endsWith(".sample")) continue;

    const targetPath = path.join(hooksTargetDir, hookName);
    let needsCopy = false;

    if (!fs.existsSync(targetPath)) {
      needsCopy = true;
    } else {
      const sourceContent = fs.readFileSync(sourcePath, "utf8");
      const targetContent = fs.readFileSync(targetPath, "utf8");
      if (sourceContent !== targetContent) {
        needsCopy = true;
      }
    }

    if (needsCopy) {
      fs.copyFileSync(sourcePath, targetPath);
      fs.chmodSync(targetPath, 0o755);
    }
  }
}

async function runSessionInit(projectDir: string): Promise<string> {
  if (cachedOutput && Date.now() - cacheTimestamp < CACHE_TTL_MS) {
    return cachedOutput;
  }

  try {
    const stdout = execSync("./.opencode/tools/session-init", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    cachedOutput = stdout;
    cacheTimestamp = Date.now();

    return stdout;
  } catch (err: any) {
    const stdout = err?.stdout?.toString().trim() ?? "";
    const stderr = err?.stderr?.toString().trim() ?? "";
    const exitCode = err?.status ?? 1;

    const bunNotFound = /bun: command not found/i.test(stderr);

    if (!stdout || stdout.length === 0) {
      const errorMsg = bunNotFound
        ? "bun runtime not found — session context unavailable. Install bun or check .opencode/tools/ensure-node for a private Node.js runtime."
        : (stderr || "Script returned empty output");
      console.error(`[session-enforcement] session-init: ${errorMsg}`);
      writeDiagnostic(projectDir, {
        source: "session-init",
        level: "error",
        message: errorMsg,
        exitCode,
      });
      if (stderr && !bunNotFound) {
        writeDiagnostic(projectDir, {
          source: "session-init",
          level: "error",
          message: stderr,
          exitCode,
        });
      }
      return "";
    }

    if (stderr) {
      writeDiagnostic(projectDir, {
        source: "session-init",
        level: "warning",
        message: stderr,
        exitCode,
      });
    }

    cachedOutput = stdout;
    cacheTimestamp = Date.now();

    return stdout;
  }
}

let cachedIdentityOutput: string | null = null;
let identityCacheTimestamp = 0;

async function runSessionContextIdentity(projectDir: string): Promise<string> {
  if (cachedIdentityOutput && Date.now() - identityCacheTimestamp < CACHE_TTL_MS) {
    return cachedIdentityOutput;
  }

  try {
    const stdout = execSync("./.opencode/scripts/session_context_identity.py", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    cachedIdentityOutput = stdout;
    identityCacheTimestamp = Date.now();

    return stdout;
  } catch (err: any) {
    const stdout = err?.stdout?.toString().trim() ?? "";
    const stderr = err?.stderr?.toString().trim() ?? "";
    const exitCode = err?.status ?? 1;

    const bunNotFound = /bun: command not found/i.test(stderr);

    if (!stdout || stdout.length === 0) {
      const errorMsg = bunNotFound
        ? "bun runtime not found — session context unavailable. Install bun or check .opencode/tools/ensure-node for a private Node.js runtime."
        : (stderr || "Script returned empty output");
      console.error(`[session-enforcement] session_context_identity.py: ${errorMsg}`);
      writeDiagnostic(projectDir, {
        source: "session_context_identity.py",
        level: "error",
        message: errorMsg,
        exitCode,
      });
      return "";
    }

    if (stderr) {
      writeDiagnostic(projectDir, {
        source: "session_context_identity.py",
        level: "warning",
        message: stderr,
        exitCode,
      });
    }

    cachedIdentityOutput = stdout;
    identityCacheTimestamp = Date.now();

    return stdout;
  }
}

let cachedTriggersOutput: string | null = null;
let triggersCacheTimestamp = 0;

async function runSessionContextTriggers(projectDir: string): Promise<string> {
  if (cachedTriggersOutput && Date.now() - triggersCacheTimestamp < CACHE_TTL_MS) {
    return cachedTriggersOutput;
  }

  try {
    const stdout = execSync("./.opencode/scripts/session_context_triggers.py", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    cachedTriggersOutput = stdout;
    triggersCacheTimestamp = Date.now();

    return stdout;
  } catch (err: any) {
    const stdout = err?.stdout?.toString().trim() ?? "";
    const stderr = err?.stderr?.toString().trim() ?? "";
    const exitCode = err?.status ?? 1;

    const bunNotFound = /bun: command not found/i.test(stderr);

    if (exitCode !== 0) {
      const errorMsg = bunNotFound
        ? "bun runtime not found — session context unavailable. Install bun or check .opencode/tools/ensure-node for a private Node.js runtime."
        : (stderr || "Script exited with non-zero code");
      console.error(`[session-enforcement] session_context_triggers.py exited with code ${exitCode}: ${errorMsg}`);
      writeDiagnostic(projectDir, {
        source: "session_context_triggers.py",
        level: "error",
        message: errorMsg,
        exitCode,
      });
      return "";
    }

    if (!stdout || stdout.length === 0) {
      if (stderr) {
        writeDiagnostic(projectDir, {
          source: "session_context_triggers.py",
          level: "warning",
          message: stderr,
          exitCode,
        });
      }
      return "";
    }

    if (stderr) {
      writeDiagnostic(projectDir, {
        source: "session_context_triggers.py",
        level: "warning",
        message: stderr,
        exitCode,
      });
    }

    cachedTriggersOutput = stdout;
    triggersCacheTimestamp = Date.now();

    return stdout;
  }
}

interface ProjectMetadata {
  name: string;
  version: string;
  pythonVersion: string;
}

function readProjectMetadata(projectDir: string): ProjectMetadata | null {
  const pyprojectPath = path.join(projectDir, "pyproject.toml");
  if (!fs.existsSync(pyprojectPath)) {
    return null;
  }

  let name = "";
  let version = "";
  let inProjectSection = false;

  try {
    const content = fs.readFileSync(pyprojectPath, "utf8");
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (trimmed === "[project]") {
        inProjectSection = true;
        continue;
      }
      if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
        inProjectSection = false;
        continue;
      }
      if (inProjectSection) {
        if (trimmed.startsWith("name")) {
          const eqIdx = trimmed.indexOf("=");
          if (eqIdx > 0) {
            name = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
          }
        } else if (trimmed.startsWith("version")) {
          const eqIdx = trimmed.indexOf("=");
          if (eqIdx > 0) {
            version = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
          }
        }
      }
    }
  } catch {
    return null;
  }

  if (!name) {
    return null;
  }

  let pythonVersion = "";
  const pythonVersionPath = path.join(projectDir, ".python-version");
  if (fs.existsSync(pythonVersionPath)) {
    try {
      pythonVersion = fs.readFileSync(pythonVersionPath, "utf8").trim();
    } catch {
      // Ignore read errors
    }
  }

  return { name, version: version || "0.1.0", pythonVersion };
}

function buildMetadataBlock(projectDir: string): string {
  const meta = readProjectMetadata(projectDir);
  if (!meta) {
    return "";
  }

  const lines: string[] = [`Project: ${meta.name} v${meta.version}`];
  if (meta.pythonVersion) {
    lines.push(`Python: ${meta.pythonVersion}`);
  }
  return lines.join("\n");
}

function buildTrainingStalenessBlock(): string {
  return `<TRAINING_STALENESS_CRITICAL>
⚠️ Your training data is STALE. You CANNOT rely on your training data for:

- API signatures, library versions, framework syntax
- Configuration formats, environment variable names
- Code patterns, best practices, recommended approaches
- Documentation, examples, tutorials

**VERIFICATION IS MANDATORY:**

1. **Check live documentation** before using any API, framework, or library
2. **Verify code signatures** using srclight_get_signature before claiming behavior
3. **Read actual source files** before asserting code behavior
4. **Confirm configuration** against live schemas before asserting compliance
5. **Attempt exhaustive research** using available tools before making factual claims; if research fails, follow suggest-after-research fallback — NEVER present training-data claims as verified facts

**DO NOT TRUST:**

- Your memory about how something works
- Code comments (they may be outdated or wrong)
- Documentation snippets from training data
- "I've seen this before" or "I know this pattern"
- Second-hand information without live source verification

**ALWAYS VERIFY** before:
- Proposing a course of action
- Providing an technical answer
- Making claims about code behavior
- Suggesting solutions

**RESEARCH-FIRST RULE:**
- General knowledge questions still require research attempts — search the web, search documentation, search the codebase
- If research tools cannot verify a claim, do NOT present it as fact with a disclaimer
- For general knowledge: offer training-data answer as suggestion contingent on user acceptance
- For code/API claims: DECLINE to state — no suggestion, no fallback, no disclaimer
- There is NO exemption for "general explanation" or "brainstorming" — research before claiming

This is a CRITICAL rule. Violations result in incorrect guidance and broken implementations.
</TRAINING_STALENESS_CRITICAL>`;
}

function buildReferencesVerificationBlock(): string {
  return `<REFERENCES_VERIFICATION_MANDATE>
⚠️ You MUST NOT assume knowledge of any referenced file, schema, configuration, or artifact without FIRST verifying its contents with a tool call. This applies to ALL activities without exception: coding, spec development, plan creation, implementation, skill book updates, runbook authoring, correspondence, and any other work.

**YOU ARE FORBIDDEN FROM:**

- Assuming you know what a file contains without opening it first
- Claiming knowledge of a schema's fields without reading the schema
- Proceeding past a reference to a file, path, or configuration without verifying the reference exists
- Treating any information as "already known" without a visible tool-call artifact proving you checked
- Writing documentation, runbooks, or specs that describe files/configs/APIs you have not actually read
- Skipping verification because "I've seen this file before" or "I know this pattern"
- Claiming a referenced file or artifact exists without confirming via glob, read, or srclight

**SELF-AUDIT GATE (MANDATORY):**

Before making ANY claim about a file, schema, configuration, or referenced artifact, you MUST produce a tool-call artifact in the conversation proving you verified it. Acceptable artifacts:

- A \`read\` tool call showing the file contents
- A \`srclight_get_signature\` or \`srclight_get_symbol\` call confirming a function/class signature
- A \`glob\` or \`grep\` call confirming a file or pattern exists
- A \`bash\` command output confirming system state

**No tool-call artifact = the claim is FORBIDDEN.** You cannot state "the config has X field" without the read call that confirmed it. You cannot state "the function takes Y parameters" without the signature lookup that verified it. You cannot state "the file exists" without the glob or read that confirmed it.

**RESEARCH-FIRST REQUIREMENT:**
Before making ANY factual claim, the agent MUST attempt exhaustive research using available tools. This includes:
- Web search for general knowledge claims
- Code search (srclight, grep, glob) for codebase claims
- Documentation lookup for API/library claims
- File read for configuration claims

If research fails, follow the suggest-after-research fallback:
- For general knowledge: Offer the training-data answer as an explicit suggestion contingent on user acceptance
- For code/API claims: DECLINE to state the claim — no suggestion, no fallback, no disclaimer

**SINGLE EXCHANGE WINDOW:** The ONLY exception is a tool call from the immediately preceding exchange (last assistant turn in the same conversation). Any earlier reference requires re-verification.

**THIS IS UNCONDITIONAL:**

- No scope exemption: applies to coding, specs, plans, runbooks, skill updates, correspondence, everything
- No activity exemption: "just checking" is not verification-free
- No knowledge exemption: "I already know this" is the specific bypass this rule closes
- No size exemption: "this is too small to verify" is not valid — verify it

**Authority:** This mandate enforces the principles in guidelines 065-verification-honesty.md (proactive verification, evidence requirement) and 075-docs-verification.md (mandatory live documentation verification). This block does not duplicate those guidelines — it operationalizes their core rules at the system-prompt level, at the exact decision point where the agent decides whether to verify or assume.
</REFERENCES_VERIFICATION_MANDATE>`;
}

function buildLanguagePreferenceBlock(): string {
  return `<LANGUAGE_PREFERENCE>
All communications MUST use **formal/business/professional Southeastern United States English**.

This means:
- Use Southern US English spelling, vocabulary, and phrasing conventions
- Maintain a formal, professional, and business-appropriate register
- Prefer clarity and directness with Southern politeness conventions
- Avoid regional colloquialisms that sacrifice professionalism
- Use "y'all" only in informal context; prefer "you" or "your team" in formal writing
</LANGUAGE_PREFERENCE>`;
}

function buildWorktreeBlock(input: PluginInput): string {
  const mainRepoDir = input?.directory || "";
  const worktreeDir = input?.worktree || "";

  if (worktreeDir && worktreeDir !== mainRepoDir) {
    return `worktree.path: ${worktreeDir}\nAll file operations (read, edit, write, glob, grep) MUST use paths prefixed with worktree.path. Relative paths resolve to the main repo, not the worktree.`;
  }

  return "";
}

/**
 * Extract and strip YAML frontmatter from SKILL.md content.
 * Adapted from obra/superpowers/plugins/superpowers.js
 */
function extractFrontmatter(content: string): {
  frontmatter: Record<string, string>;
  body: string;
} {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: content };

  const frontmatterStr = match[1];
  const body = match[2];
  const frontmatter: Record<string, string> = {};

  for (const line of frontmatterStr.split("\n")) {
    const colonIdx = line.indexOf(":");
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, "");
      frontmatter[key] = value;
    }
  }

  return { frontmatter, body };
}

interface FrontmatterError {
  skillDir: string;
  issues: string[];
}

/**
 * Load skill descriptions from YAML frontmatter in SKILL.md files.
 * Adapted from obra/superpowers/plugins/superpowers.js skill discovery pattern.
 *
 * Source attribution: CSO (Content Search Optimization) principles from
 * https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md
 * Description format: "Use when..." with triggering conditions, NOT workflow summaries.
 *
 * Returns { skills, errors } where errors collects frontmatter validation issues.
 * See #601 for the original bug that motivated frontmatter validation.
 */
function loadSkillDescriptions(skillsDir: string): {
  skills: Array<{ name: string; description: string }>;
  errors: FrontmatterError[];
} {
  const skills: Array<{ name: string; description: string }> = [];
  const errors: FrontmatterError[] = [];

  try {
    const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(skillsDir, entry.name, "SKILL.md");
      if (!fs.existsSync(skillPath)) continue;

      try {
        const content = fs.readFileSync(skillPath, "utf8");
        const validationIssues: string[] = [];

        const hasOpeningDelimiter = /^---\s*\n/m.test(content);
        const { frontmatter } = extractFrontmatter(content);

        if (!hasOpeningDelimiter) {
          validationIssues.push("Missing `---` opening delimiter");
        } else if (Object.keys(frontmatter).length === 0) {
          validationIssues.push("Delimiters present but no key:value pairs parsed (format error)");
        }

        if (hasOpeningDelimiter && !frontmatter.name) {
          validationIssues.push("Missing `name` field");
        }

        if (hasOpeningDelimiter && !frontmatter.description) {
          validationIssues.push("Missing `description` field — skill will be invisible to enforcement");
        } else if (frontmatter.description && !frontmatter.description.startsWith("Use when")) {
          validationIssues.push("Description does not start with \"Use when\" — CSO requirement for trigger discovery");
        }

        if (validationIssues.length > 0) {
          errors.push({ skillDir: entry.name, issues: validationIssues });
        }

        const name = frontmatter.name || entry.name;
        const description = frontmatter.description || "";
        if (description) {
          skills.push({ name, description });
        }
      } catch {
        // Skip unreadable skill files
      }
    }
  } catch {
    // Skills directory may not exist in all contexts
  }

  return { skills, errors };
}

/**
 * Build a structured warning string for frontmatter validation errors.
 * Returns empty string if no errors, so the caller can skip injection.
 * References #601 as the example bug that motivated this validation.
 */
function buildFrontmatterWarning(errors: FrontmatterError[]): string {
  if (errors.length === 0) return "";

  const perSkillListing = errors
    .map(e => `- **${e.skillDir}**: ${e.issues.join("; ")}`)
    .join("\n");

  return `<FRONTMATTER_VALIDATION_WARNING>
⚠️ The following SKILL.md files have frontmatter issues that may make skills invisible to enforcement:

${perSkillListing}

**Fix template** — every SKILL.md MUST start with this YAML frontmatter block:

\`\`\`yaml
---
name: skill-name
description: Use when [triggering conditions]. Triggers on: [keywords].
type: discipline-enforcing
license: MIT
---
\`\`\`

See #601 for the original bug that motivated this validation.
</FRONTMATTER_VALIDATION_WARNING>`;
}

/**
 * Regex matching a bare issue reference: input that is solely an issue number
 * like `#591`. Does NOT match `fix #591`, `see #591 and #592`, or any
 * message with additional context.
 */
const BARE_ISSUE_RE = /^\s*#(\d+)\s*$/;

/**
 * Build a pipeline directive for bare issue references.
 * When a user sends just `#N`, the agent should follow a deterministic
 * audit→brainstorm→plan→HALT pipeline rather than guessing.
 */
function buildIssuePipelineDirective(issueNumber: string): string {
  return `<ISSUE_PIPELINE_TRIGGER>
The user provided a bare issue reference #${issueNumber}. Follow this mandatory pipeline:

1. **Read the issue**: Use github_issue_read with method=get AND method=get_comments for #${issueNumber}
2. **Audit the spec**: Invoke /skill spec-auditor --issue ${issueNumber}
3. **Brainstorm refinements**: Invoke /skill brainstorming
4. **Write a plan**: Invoke /skill writing-plans --task create
5. **HALT** — Never auto-execute. Wait for explicit authorization.

Critical rules:
- Never auto-execute any plan
- Follow each skill's own protocol
- Adapt for bug reports (audit still runs, brainstorming explores the bug)
- Fix audit findings before brainstorming
- Read ALL comments on the issue before acting
</ISSUE_PIPELINE_TRIGGER>`;
}

/**
 * Build the enforcement content injected into the first user message.
 *
 * Adapted from obra/superpowers skill enforcement pattern:
 * https://github.com/obra/superpowers/blob/main/.opencode/plugins/superpowers.js
 *
 * Key principle: "If you think there is even a 1% chance a skill might apply,
 * you ABSOLUTELY MUST invoke the skill." — from obra/superpowers using-superpowers
 */
function buildEnforcementContent(skillDescriptions: Array<{ name: string; description: string }>): string {
  // Process skills first, implementation skills second (adapted from superpowers priority)
  const processSkills = skillDescriptions.filter(s =>
    ["approval-gate", "brainstorming", "spec-creation", "writing-plans", "executing-plans",
     "verification-before-completion", "finishing-a-development-branch",
     "git-workflow", "using-git-worktrees", "systematic-debugging", "spec-auditor",
     "issue-operations"].includes(s.name)
  );
  const implSkills = skillDescriptions.filter(s => !processSkills.includes(s));

  const sortedSkills = [...processSkills, ...implSkills];

  const skillLines = sortedSkills
    .map(s => `- **${s.name}**: ${s.description}`)
    .join("\n");

  // Red-flags rationalization table adapted from obra/superpowers writing-skills SKILL.md
  // https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md
  return `<EXTREMELY_IMPORTANT>
You have access to mandatory workflow skills. Skill invocation is NOT optional when a skill applies.

**The 1% Rule:** If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.

## Skill Priority

When multiple skills could apply, use this order:

1. **Process skills first** (approval-gate, brainstorming, spec-creation, issue-operations, writing-plans, systematic-debugging) — these determine HOW to approach the task
2. **Implementation skills second** — these guide execution

## Red Flags — STOP and Invoke the Skill

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Default Operating Mode: Discussion

You are in **discussion mode** by default. This means:

- **Valid actions**: Read, analyze, brainstorm, review, plan, answer questions
- **NOT valid**: Implementation — writing code, editing files, creating branches, or making any changes
- **Authorization required**: Only explicit "approved" or "go" transitions you to action mode for the specific authorized task
- **Discussion conclusions are NOT authorization**: Reaching agreement on an approach does NOT authorize implementation
- **Task-scoped authorization**: After completing an authorized task, you return to discussion mode automatically
- **No proactive suggestions**: After completing a task, do not suggest next steps or propose additional work

## Available Skills

${skillLines}

## How to Invoke Skills

Use the OpenCode skill tool: \`/skill <skill-name>\` or \`/skill <skill-name> --task <task-name>\`

Invoke relevant skills BEFORE any response or action. Even a 1% chance means invoke it to check.
</EXTREMELY_IMPORTANT>`;
}

function extractValue(sessionOutput: string | null, key: string): string | null {
  if (!sessionOutput) return null;
  const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = sessionOutput.match(new RegExp(`${escapedKey}=\\s*(\\S+)`));
  return match ? match[1] : null;
}

function detectAgentBinary(): { name: string; version: string } {
  const argv0 = process.argv[0] || "";
  const argv1 = process.argv[1] || "";

  for (const arg of [argv1, argv0]) {
    if (arg.includes("opencode-cli")) {
      return { name: "OpenCode CLI", version: "" };
    }
    if (arg.includes("opencode") || arg.includes("OpenCode")) {
      return { name: "OpenCode", version: "" };
    }
  }

  const envBinary = process.env.OPENCODE_BINARY || "";
  const envVersion = process.env.OPENCODE_VERSION || "";

  if (envBinary) {
    return { name: envBinary, version: envVersion || "" };
  }

  return { name: "unknown (version detection failed)", version: "" };
}

function buildIdentityEchoDirective(platform: string, owner: string, repo: string, agentName?: string, modelId?: string): string {
  const agentLine = `🤖 ${agentName || "<AgentName>"} (${modelId || "<ModelId>"}) <status-icon> <status>`;

  return `<IDENTITY_ECHO>
Before doing anything else, you MUST echo your platform identity as your very first output. The CORRECT values are:

Platform: ${platform}, Org: ${owner}, Repo: ${repo}

You MUST output EXACTLY these values in this format:
Platform: ${platform}, Org: ${owner}, Repo: ${repo}
${agentLine}

⚠️ FATAL: If your echo does not match Platform: ${platform}, Org: ${owner}, Repo: ${repo} character-for-character, you MUST HALT immediately and report the mismatch. Do NOT proceed with any operations with incorrect identity. Do NOT infer identity from repository names, file paths, or environment variables. Use ONLY the values provided in the system prompt identity section.

After the identity echo, acknowledge any trigger warnings from the SESSION_TRIGGERS block above.
</IDENTITY_ECHO>`;
}

/**
 * Secret patterns for redaction.
 * These regexes match secret values in various formats while preserving key names.
 */
const SECRET_PATTERNS: Array<{ pattern: RegExp; type: string }> = [
  { pattern: /\b(TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL|API_KEY|PRIVATE_KEY|ACCESS_TOKEN)\s*[=:]\s*["']?([^\s"']+?)["']?(?=\s|$|[^\w])/gi, type: "assignment" },
  { pattern: /:\/\/([^:]+):([^@]+)@/g, type: "url_password" },
  { pattern: /\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}/g, type: "github_token" },
  { pattern: /\bglpat-[A-Za-z0-9\-]{20,}/g, type: "gitlab_token" },
];

/**
 * Redact secrets from text, replacing values with [REDACTED:TYPE] markers.
 * Key names are preserved — only secret values are replaced.
 *
 * Co-authored with AI: OpenCode (ollama-cloud/glm-5)
 */
function redactSecrets(text: string): string {
  let result = text;

  // URL-embedded passwords: user:password@ → user:[REDACTED:PASSWORD]@
  result = result.replace(/:\/\/([^:]+):([^@]+)@/g, (_match, user: string, _password: string) => {
    return `://${user}:[REDACTED:PASSWORD]@`;
  });

  // GitHub tokens
  result = result.replace(/\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}/g, "[REDACTED:TOKEN]");

  // GitLab tokens
  result = result.replace(/\bglpat-[A-Za-z0-9\-]{20,}/g, "[REDACTED:TOKEN]");

  // Assignment patterns: KEY=value, KEY="value", KEY='value'
  // Matches keys that end with or are exactly one of the secret keywords
  // e.g., GITBUCKET_TOKEN=value, MY_SECRET=value, PASSWORD=abc, API_KEY="xyz"
  result = result.replace(
    /((?:\w*(?:TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL|API_KEY|PRIVATE_KEY|ACCESS_TOKEN))\s*[=:]\s*)(["']?)([^\s"'#]+?)\2/gi,
    (_match, prefix: string, quote: string, _value: string) => {
      const keyMatch = prefix.match(/(\w+)\s*[=:]/);
      const keyName = keyMatch ? keyMatch[1].toUpperCase() : "";
      let typeLabel: string;
      if (keyName === "PASSWORD" || keyName === "CREDENTIAL") {
        typeLabel = keyName;
      } else if (keyName.endsWith("PASSWORD")) {
        typeLabel = "PASSWORD";
      } else if (keyName.endsWith("CREDENTIAL")) {
        typeLabel = "CREDENTIAL";
      } else {
        typeLabel = "TOKEN";
      }
      return `${prefix}${quote}[REDACTED:${typeLabel}]${quote}`;
    }
  );

  return result;
}

/**
 * Build a protected branch edit warning block for when files are edited
 * on dev/main without a worktree or pair- branch prefix.
 * 
 * This is the per-turn runtime guard — it fires AFTER each assistant turn
 * when git diff detects file changes on a protected branch. This is distinct
 * from the session-start trigger in session_context_triggers.py which only
 * checks once at session start.
 */
function buildProtectedBranchEditWarning(changedFiles: string[], branch: string): string {
  const fileList = changedFiles.slice(0, 10).map(f => `  - \`${f}\``).join("\n");
  const moreFiles = changedFiles.length > 10 ? `\n  - ... and ${changedFiles.length - 10} more` : "";
  
  return `<PROTECTED_BRANCH_EDIT_WARNING>
⚠️ CRITICAL: Files were edited on branch \`${branch}\` without a worktree or pair-mode prefix.

This is a CRITICAL GUIDELINE VIOLATION. Edits on \`dev\` or \`main\` outside a worktree risk:
- Corrupting the shared development branch
- Losing changes when switching branches
- Conflicting with other developers' work

${changedFiles.length} file(s) changed:
${fileList}${moreFiles}

**MANDATORY RECOVERY:**
1. STOP all further edits immediately
2. Stash or revert the unintended changes: \`git stash\` or \`git checkout -- .\`
3. Create a proper feature branch in a worktree: invoke \`git-workflow --task pre-work\`
4. Only resume implementation in the worktree

The only exception: if the branch starts with \`pair-\` (pair-mode collaboration), 
edits on the development branch are expected and this warning should not fire.
</PROTECTED_BRANCH_EDIT_WARNING>`;
}

/**
 * Detect uncommitted file changes on the current branch via git diff.
 * Returns empty array if no changes or if git is unavailable.
 */
function detectUncommittedFileChanges(projectDir: string): string[] {
  try {
    const result = execSync("git diff --name-only", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
    if (!result) return [];
    return result.split("\n").filter(line => line.trim().length > 0);
  } catch {
    return [];
  }
}

/**
 * Get the current git branch name.
 * Returns null if git is unavailable.
 */
function getCurrentBranch(projectDir: string): string | null {
  try {
    return execSync("git branch --show-current", {
      cwd: projectDir,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim() || null;
  } catch {
    return null;
  }
}

/**
 * Check if the current branch is a protected branch (main/master/dev)
 * that should not have direct edits.
 */
function isProtectedBranch(branch: string): boolean {
  return branch === "main" || branch === "master" || branch === "dev";
}

/**
 * Check if the current branch is a pair-mode branch (starts with "pair-").
 * Pair-mode branches allow direct edits on the development directory.
 */
function isPairModeBranch(branch: string): boolean {
  return branch.startsWith("pair-");
}

export default async function sessionEnforcementPlugin(input: PluginInput): Promise<Hooks> {
  // Determine skills directory and project directory
  const projectDir = input?.directory || process.cwd();
  const skillsDir = path.join(projectDir, ".opencode", "skills");

  // Pre-load skill descriptions and frontmatter validation at plugin startup
  const { skills: skillDescriptions, errors: frontmatterErrors } = loadSkillDescriptions(skillsDir);

  // Ensure git hooks from .opencode/hooks/ are installed into .git/hooks/
  ensureHooksInstalled(projectDir);

  return {
    // Inject session context into system prompt (from session-init + PluginInput augmentations)
    "experimental.chat.system.transform": async (sysInput, output) => {
      // --- Sub-agent session detection (REQ-1/REQ-5) ---
      // Query client.session.get() for parentID; if present, this session
      // is a sub-agent. Register in process-scoped Set for later use in
      // messages.transform. Graceful degradation: on failure, assume
      // primary session (REQ-4).
      const sessionID = sysInput?.sessionID;
      if (sessionID) {
        try {
          const sessionResult = await input.client.session.get({
            path: { id: sessionID },
          });
          if (sessionResult.data?.parentID) {
            subAgentSessions.add(sessionID);
          } else {
            subAgentSessions.delete(sessionID);
          }
        } catch {
          // REQ-4: Graceful degradation — assume primary session on API failure
          subAgentSessions.delete(sessionID);
        }
      }

      const scriptOutput = await runSessionInit(projectDir);
      if (scriptOutput) {
        output.system.push(scriptOutput);
      }

      // Inject worktree context when session is operating in a worktree
      const worktreeBlock = buildWorktreeBlock(input);
      if (worktreeBlock) {
        output.system.push(worktreeBlock);
      }

      // Inject project metadata (name, version, Python version)
      const metadataBlock = buildMetadataBlock(projectDir);
      if (metadataBlock) {
        output.system.push(metadataBlock);
      }

      // Inject training staleness warning (verifying everything is mandatory)
      output.system.push(buildTrainingStalenessBlock());

      // Inject references verification mandate (no assuming knowledge without tool-call artifact)
      output.system.push(buildReferencesVerificationBlock());

      // Inject language preference (Southeastern US English mandate)
      output.system.push(buildLanguagePreferenceBlock());

      // Inject frontmatter validation warning if any skills have broken frontmatter
      const warning = buildFrontmatterWarning(frontmatterErrors);
      if (warning) {
        output.system.push(warning);
      }

      // Inject identity section from session_context_identity.py
      const identityOutput = await runSessionContextIdentity(projectDir);
      if (identityOutput) {
        output.system.push(identityOutput);
      }

      // Inject agent binary name and version for LLM identity echo
      const agentBinary = detectAgentBinary();
      const agentBlock = [`AgentName: ${agentBinary.name}`];
      if (agentBinary.version) {
        agentBlock.push(`ModelId: ${agentBinary.version}`);
      }
      output.system.push(agentBlock.join("\n"));
    },

    // Inject enforcement content into first user message (adapted from obra/superpowers)
      // AND detect bare #N issue references in last user message
      // AND inject identity-echo directive + trigger warnings into first user message
      // AND inject plugin diagnostics block into first user message
      //
      // FIRST-TURN GUARD: IDENTITY_ECHO, SESSION_TRIGGERS, EXTREMELY_IMPORTANT,
      // PLUGIN_DIAGNOSTICS, and IDENTITY_VALIDATION_FAILURE are injected ONLY on
      // the first turn (when userMessages.length === 1). This prevents context
      // window bloat from accumulated re-injected blocks on subsequent turns.
      //
      // Per-turn behaviors (unchanged):
      // - Bare issue pipeline detection on lastUser
      // - Secret redaction on all assistant messages
      "experimental.chat.messages.transform": async (_input, output) => {
        if (!output.messages || !output.messages.length) return;

        const userMessages = output.messages.filter(m => m.info?.role === "user");
        if (!userMessages.length) return;

        const firstUser = userMessages[0];
        const isFirstTurn = userMessages.length === 1;

        // --- First-turn-only: Enforcement injection into FIRST user message ---
        if (isFirstTurn) {
          const enforcementContent = buildEnforcementContent(skillDescriptions);
          if (enforcementContent && firstUser.parts?.length) {
            if (!firstUser.parts.some(p => p.type === "text" && p.text?.includes("EXTREMELY_IMPORTANT"))) {
              const ref = firstUser.parts[0];
              firstUser.parts.unshift({ ...ref, type: "text", text: enforcementContent });
            }
          }

          // --- First-turn-only: Identity-echo directive + trigger warnings ---
          const triggersOutput = await runSessionContextTriggers(projectDir);
          const knownPlatform = extractValue(cachedIdentityOutput, "github.platform");
          const knownOwner = extractValue(cachedIdentityOutput, "github.owner");
          const knownRepo = extractValue(cachedIdentityOutput, "github.repo");

          // Detect agent binary for identity echo
          const agentBinary = detectAgentBinary();

          const identityBlock = buildIdentityEchoDirective(
            knownPlatform || "<platform>",
            knownOwner || "<owner>",
            knownRepo || "<repo>",
            agentBinary.name,
            agentBinary.version || undefined,
          );
          const triggerBlock = triggersOutput ? `<SESSION_TRIGGERS>\n${triggersOutput}\n</SESSION_TRIGGERS>` : "";

          const echoParts: string[] = [];
          if (identityBlock) {
            echoParts.push(identityBlock);
          }
          if (triggerBlock) {
            echoParts.push(triggerBlock);
          }
          if (echoParts.length > 0 && firstUser.parts?.length) {
            firstUser.parts.unshift({ type: "text", text: echoParts.join("\n\n") });
          }

          // --- First-turn-only: Plugin diagnostics injection ---
          const diagnostics = collectDiagnostics(projectDir);
          const diagnosticBlock = buildDiagnosticBlock(diagnostics);
          if (diagnosticBlock && firstUser.parts?.length) {
            firstUser.parts.push({ type: "text", text: diagnosticBlock });
          }

          // --- First-turn-only: Identity echo validation ---
          if (!knownPlatform || !knownOwner || !knownRepo) {
            const missing = [
              !knownPlatform ? "github.platform" : null,
              !knownOwner ? "github.owner" : null,
              !knownRepo ? "github.repo" : null,
            ].filter(Boolean).join(", ");

            const lastUser = userMessages[userMessages.length - 1];
            if (lastUser?.parts?.length) {
              lastUser.parts.push({
                type: "text",
                text: `<IDENTITY_VALIDATION_FAILURE>\n⚠️ FATAL: Session identity values are MISSING. HALT all operations immediately.\n\nMissing values: ${missing}\n\nIdentity validation cannot proceed without these values. Do NOT infer identity from repository names, file paths, or environment variables. Resolve the missing identity values before continuing any operations.\n</IDENTITY_VALIDATION_FAILURE>`
              });
            }
          } else {
            const assistantMessages = output.messages.filter(m => m.info?.role === "assistant");
            if (assistantMessages.length > 0) {
              const firstAssistant = assistantMessages[0];
              const assistantText = firstAssistant.parts
                ?.filter(p => p.type === "text" && p.text)
                .map(p => p.text)
                .join(" ") || "";

              const echoMatch = assistantText.match(/Platform:\s*(\S+),\s*Org:\s*(\S+),\s*Repo:\s*(\S+)/);

              const lastUser = userMessages[userMessages.length - 1];

              if (!echoMatch) {
                if (lastUser?.parts?.length) {
                  lastUser.parts.push({
                    type: "text",
                    text: `<IDENTITY_VALIDATION_FAILURE>\n⚠️ FATAL: Your first message did not contain a valid identity echo. You MUST echo your platform identity before proceeding with ANY operations.\n\nExpected: Platform: ${knownPlatform}, Org: ${knownOwner}, Repo: ${knownRepo}\n\nHALT all operations. Echo the correct identity values above before continuing.\n</IDENTITY_VALIDATION_FAILURE>`
                  });
                }
              } else {
                const [, echoPlatform, echoOwner, echoRepo] = echoMatch;
                if (echoPlatform !== knownPlatform || echoOwner !== knownOwner || echoRepo !== knownRepo) {
                  if (lastUser?.parts?.length) {
                    lastUser.parts.push({
                      type: "text",
                      text: `<IDENTITY_VALIDATION_FAILURE>\n⚠️ FATAL: Identity echo mismatch detected!\n\nYour echo: Platform: ${echoPlatform}, Org: ${echoOwner}, Repo: ${echoRepo}\nExpected: Platform: ${knownPlatform}, Org: ${knownOwner}, Repo: ${knownRepo}\n\nHALT all operations. These values do NOT match. Use ONLY the expected values above. Do NOT infer identity from repository names, file paths, or environment variables.\n</IDENTITY_VALIDATION_FAILURE>`
                    });
                  }
                }
              }
            }
          }
        }

      // --- Per-turn: Bare issue pipeline detection on LAST user message ---
      const lastUser = userMessages[userMessages.length - 1];
      if (lastUser?.parts?.length) {
        for (const part of lastUser.parts) {
          if (part.type === "text" && part.text) {
            const match = part.text.match(BARE_ISSUE_RE);
            if (match) {
              const directive = buildIssuePipelineDirective(match[1]);
              lastUser.parts.push({ type: "text", text: directive });
              break; // Only inject pipeline directive once per message
            }
          }
        }
      }

      // --- Per-turn: Secret redaction on ALL assistant messages ---
      const assistantMessages = output.messages.filter(m => m.info?.role === "assistant");
      for (const msg of assistantMessages) {
        if (!msg.parts?.length) continue;
        for (let i = 0; i < msg.parts.length; i++) {
          const part = msg.parts[i];
          if (part.type === "text" && part.text) {
            const redacted = redactSecrets(part.text);
            if (redacted !== part.text) {
              msg.parts[i] = { ...part, type: "text", text: redacted };
            }
          }
        }
      }

      // --- Per-turn: Protected branch edit guard ---
      // After each assistant turn, check if files were edited on dev/main
      // without a worktree or pair- branch prefix. If so, inject warning.
      const currentBranch = getCurrentBranch(projectDir);
      if (currentBranch && isProtectedBranch(currentBranch)) {
        const worktreeDir = input?.worktree || "";
        const inWorktree = worktreeDir && worktreeDir !== projectDir;
        
        if (!inWorktree && !isPairModeBranch(currentBranch)) {
          const changedFiles = detectUncommittedFileChanges(projectDir);
          if (changedFiles.length > 0) {
            const warning = buildProtectedBranchEditWarning(changedFiles, currentBranch);
            const lastAssistant = assistantMessages[assistantMessages.length - 1];
            if (lastAssistant?.parts?.length) {
              lastAssistant.parts.push({ type: "text", text: warning });
            }
          }
        }
      }
    },
  };
}
