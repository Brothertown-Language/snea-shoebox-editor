/**
 * Session Enforcement Plugin for OpenCode
 *
 * Unified plugin that combines session initialization and skill enforcement
 * injection. Replaces the retired session-init.ts plugin.
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

const SCRIPT_PATH = ".opencode/scripts/session_init.py";
const CACHE_TTL_MS = 5 * 60 * 1000;

let cachedOutput: string | null = null;
let cachedEnv: Record<string, string> | null = null;
let cacheTimestamp = 0;

function parseEnvFromOutput(stdout: string): Record<string, string> {
  const env: Record<string, string> = {};
  for (const line of stdout.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.includes("=") && !trimmed.startsWith("#")) {
      const eqIdx = trimmed.indexOf("=");
      const key = trimmed.slice(0, eqIdx).trim();
      const value = trimmed.slice(eqIdx + 1).trim();
      if (key && value !== undefined) {
        env[key] = value;
      }
    }
  }
  return env;
}

async function runSessionInit($: PluginInput["$"]): Promise<{
  output: string;
  env: Record<string, string>;
}> {
  if (cachedOutput && Date.now() - cacheTimestamp < CACHE_TTL_MS) {
    return { output: cachedOutput, env: cachedEnv! };
  }

  try {
    const result = await $.nothrow()`uv run python ${SCRIPT_PATH}`;
    const stdout = result.text();

    if (!stdout || stdout.trim().length === 0) {
      console.error("[session-enforcement] Script returned empty output");
      return { output: "", env: {} };
    }

    if (result.exitCode !== 0) {
      const stderr = result.stderr.toString();
      console.error(`[session-enforcement] Script exited with code ${result.exitCode}: ${stderr}`);
      return { output: "", env: {} };
    }

    const env = parseEnvFromOutput(stdout);

    cachedOutput = stdout;
    cachedEnv = env;
    cacheTimestamp = Date.now();

    return { output: stdout, env };
  } catch (err) {
    console.error("[session-enforcement] Failed to run session_init.py:", err);
    return { output: "", env: {} };
  }
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
 * https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
 *
 * Key principle: "If you think there is even a 1% chance a skill might apply,
 * you ABSOLUTELY MUST invoke the skill." — from obra/superpowers using-superpowers
 */
function buildEnforcementContent(skillDescriptions: Array<{ name: string; description: string }>): string {
  // Process skills first, implementation skills second (adapted from superpowers priority)
  const processSkills = skillDescriptions.filter(s =>
    ["approval-gate", "brainstorming", "writing-plans", "executing-plans",
     "verification-before-completion", "finishing-a-development-branch",
     "git-workflow", "systematic-debugging", "spec-auditor",
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

## Available Skills

${skillLines}

## How to Invoke Skills

Use the OpenCode skill tool: \`/skill <skill-name>\` or \`/skill <skill-name> --task <task-name>\`

Invoke relevant skills BEFORE any response or action. Even a 1% chance means invoke it to check.
</EXTREMELY_IMPORTANT>`;
}

export default async function sessionEnforcementPlugin(input: PluginInput): Promise<Hooks> {
  // Determine skills directory
  const projectDir = input?.directory || process.cwd();
  const skillsDir = path.join(projectDir, ".opencode", "skills");

  // Pre-load skill descriptions and frontmatter validation at plugin startup
  const { skills: skillDescriptions, errors: frontmatterErrors } = loadSkillDescriptions(skillsDir);

  return {
    // Inject session context into system prompt (absorbed from session-init.ts)
    "experimental.chat.system.transform": async (_input, output) => {
      const { output: scriptOutput } = await runSessionInit(input.$);
      if (scriptOutput) {
        output.system.push(scriptOutput);
      }

      // Inject frontmatter validation warning if any skills have broken frontmatter
      const warning = buildFrontmatterWarning(frontmatterErrors);
      if (warning) {
        output.system.push(warning);
      }
    },

    // Inject environment variables (absorbed from session-init.ts)
    "shell.env": async (_input, output) => {
      const { env } = await runSessionInit(input.$);
      for (const [key, value] of Object.entries(env)) {
        output.env[key] = value;
      }
    },

    // Inject enforcement content into first user message (adapted from obra/superpowers)
    // AND detect bare #N issue references in last user message
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