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

let cachedOutput: string | null = null;
let cacheTimestamp = 0;

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
    return;
  }

  const gitDir = resolveGitDir(projectDir);
  if (!gitDir) {
    console.error("[session-enforcement] Could not resolve .git directory for hooks installation");
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

async function runSessionInit($: PluginInput["$"]): Promise<string> {
  if (cachedOutput && Date.now() - cacheTimestamp < CACHE_TTL_MS) {
    return cachedOutput;
  }

  try {
    const result = await $.nothrow()`./.opencode/tools/session-init`;
    const stdout = result.text();

    if (!stdout || stdout.trim().length === 0) {
      console.error("[session-enforcement] Script returned empty output");
      return "";
    }

    if (result.exitCode !== 0) {
      const stderr = result.stderr.toString();
      console.error(`[session-enforcement] Script exited with code ${result.exitCode}: ${stderr}`);
      return "";
    }

    cachedOutput = stdout;
    cacheTimestamp = Date.now();

    return stdout;
  } catch (err) {
    console.error("[session-enforcement] Failed to run session-init:", err);
    return "";
  }
}

let cachedIdentityOutput: string | null = null;
let identityCacheTimestamp = 0;

async function runSessionContextIdentity($: PluginInput["$"]): Promise<string> {
  if (cachedIdentityOutput && Date.now() - identityCacheTimestamp < CACHE_TTL_MS) {
    return cachedIdentityOutput;
  }

  try {
    const result = await $.nowrap()`./.opencode/scripts/session_context_identity.py`;
    const stdout = result.text();

    if (result.exitCode !== 0) {
      console.error(`[session-enforcement] session_context_identity.py exited with code ${result.exitCode}: ${result.stderr.toString()}`);
      return "";
    }

    if (!stdout || stdout.trim().length === 0) {
      return "";
    }

    cachedIdentityOutput = stdout;
    identityCacheTimestamp = Date.now();

    return stdout;
  } catch (err) {
    console.error("[session-enforcement] Failed to run session_context_identity.py:", err);
    return "";
  }
}

let cachedTriggersOutput: string | null = null;
let triggersCacheTimestamp = 0;

async function runSessionContextTriggers($: PluginInput["$"]): Promise<string> {
  if (cachedTriggersOutput && Date.now() - triggersCacheTimestamp < CACHE_TTL_MS) {
    return cachedTriggersOutput;
  }

  try {
    const result = await $.nothrow()`./.opencode/scripts/session_context_triggers.py`;
    const stdout = result.text();

    if (result.exitCode !== 0) {
      console.error(`[session-enforcement] session_context_triggers.py exited with code ${result.exitCode}: ${result.stderr.toString()}`);
      return "";
    }

    if (!stdout || stdout.trim().length === 0) {
      return "";
    }

    cachedTriggersOutput = stdout;
    triggersCacheTimestamp = Date.now();

    return stdout;
  } catch (err) {
    console.error("[session-enforcement] Failed to run session_context_triggers.py:", err);
    return "";
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
5. **Tag unverified assertions** as "(unverified)" if you cannot verify them

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

This is a CRITICAL rule. Violations result in incorrect guidance and broken implementations.
</TRAINING_STALENESS_CRITICAL>`;
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
    ["approval-gate", "brainstorming", "writing-plans", "executing-plans",
     "verification-before-completion", "finishing-a-development-branch",
     "git-workflow", "using-git-worktrees", "systematic-debugging", "spec-auditor",
     "github-issue-creation", "github-sub-issues"].includes(s.name)
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

1. **Process skills first** (approval-gate, brainstorming, writing-plans, systematic-debugging) — these determine HOW to approach the task
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

function buildIdentityEchoDirective(): string {
  return `<IDENTITY_ECHO>
Before doing anything else, you MUST echo your platform identity as your very first output. Read the values from the system prompt dotted pairs (github.platform, github.owner, github.repo) and output them in this exact format:

Platform: <platform>, Org: <owner>, Repo: <repo>
🤖 <AgentName> (<ModelId>) <status-icon> <status>

Example: Platform: github, Org: Brothertown-Language, Repo: snea-shoebox-editor
🤖 OpenCode (ollama-cloud/glm-5) ✅ ready

The directive does NOT contain actual values — you MUST read github.platform, github.owner, and github.repo from the system prompt dotted pairs above. This ensures you have read and acknowledged the correct owner/repo before making any API calls.

After the identity echo, acknowledge any trigger warnings from the SESSION_TRIGGERS block above.
</IDENTITY_ECHO>`;
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
    "experimental.chat.system.transform": async (_input, output) => {
      const scriptOutput = await runSessionInit(input.$);
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

      // Inject language preference (Southeastern US English mandate)
      output.system.push(buildLanguagePreferenceBlock());

      // Inject frontmatter validation warning if any skills have broken frontmatter
      const warning = buildFrontmatterWarning(frontmatterErrors);
      if (warning) {
        output.system.push(warning);
      }

      // Inject identity section from session_context_identity.py
      const identityOutput = await runSessionContextIdentity(input.$);
      if (identityOutput) {
        output.system.push(identityOutput);
      }
    },

    // Inject enforcement content into first user message (adapted from obra/superpowers)
      // AND detect bare #N issue references in last user message
      // AND inject identity-echo directive + trigger warnings into first user message
      "experimental.chat.messages.transform": async (_input, output) => {
        if (!output.messages || !output.messages.length) return;

        const userMessages = output.messages.filter(m => m.info?.role === "user");
        if (!userMessages.length) return;

        const firstUser = userMessages[0];

        // --- Enforcement injection into FIRST user message ---
        const enforcementContent = buildEnforcementContent(skillDescriptions);
        if (enforcementContent && firstUser.parts?.length) {
          if (!firstUser.parts.some(p => p.type === "text" && p.text?.includes("EXTREMELY_IMPORTANT"))) {
            const ref = firstUser.parts[0];
            firstUser.parts.unshift({ ...ref, type: "text", text: enforcementContent });
          }
        }

        // --- Identity-echo directive + trigger warnings injection into FIRST user message ---
        const triggersOutput = await runSessionContextTriggers(input.$);
        const identityBlock = buildIdentityEchoDirective();
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

      // --- Bare issue pipeline detection on LAST user message ---
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
    },
  };
}
