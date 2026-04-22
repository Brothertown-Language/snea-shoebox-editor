/**
 * Env-Loader Plugin for OpenCode
 *
 * Reads project environment data and injects all key-value pairs into
 * every shell session via the `shell.env` hook. This is the SOLE provider
 * of bash environment variables — session-enforcement.ts owns LLM context.
 *
 * Sources (independently gathered, no cross-plugin coupling):
 * - .env file — all parsed key-value pairs including secrets
 * - input.worktree — WORKTREE_PATH for bash commands
 * - input.$ (git) — BRANCH_NAME, GIT_OWNER, GIT_REPO, GIT_PLATFORM,
 *   DEV_NAME, DEV_EMAIL, GITHUB_HTML_URL, GITBUCKET_HTML_URL,
 *   GITBUCKET_SSH_URL, GITBUCKET_HAS_CREDENTIALS
 *
 * Hook: shell.env ONLY — no system.transform, no LLM output.
 *
 * Restored from commit f7555bd, extended per issue #712.
 *
 * Co-authored with AI: OpenCode (ollama-cloud/glm-5)
 */

import type { Hooks, PluginInput } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

const ENV_FILE = ".env";

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

interface ParseResult {
  env: Record<string, string>;
  warnings: string[];
}

function parseEnvFile(content: string): ParseResult {
  const env: Record<string, string> = {};
  const warnings: string[] = [];

  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim();

    if (line === "" || line.startsWith("#")) {
      continue;
    }

    const eqIdx = line.indexOf("=");
    if (eqIdx === -1) {
      continue;
    }

    const key = line.slice(0, eqIdx).trim();
    let value = line.slice(eqIdx + 1).trim();

    if (!key) {
      continue;
    }

    // Strip inline comments before unquoting
    value = stripInlineComments(value);

    // Strip surrounding quotes
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    if (key in env) {
      warnings.push(`Duplicate key "${key}" — last value wins`);
    }

    env[key] = value;
  }

  return { env, warnings };
}

function stripInlineComments(value: string): string {
  // If value is quoted, don't strip inline comments — hashes inside quotes are literal
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value;
  }
  // For unquoted values, strip inline comments: `value # comment`
  const hashIdx = value.indexOf(" #");
  if (hashIdx !== -1) {
    return value.slice(0, hashIdx).trim();
  }
  return value;
}

function isEnvGitignored(projectDir: string): boolean {
  const gitignorePath = path.join(projectDir, ".gitignore");
  try {
    const content = fs.readFileSync(gitignorePath, "utf8");
    const lines = content.split("\n");
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed === ".env" || trimmed === "/.env") {
        return true;
      }
    }
    return false;
  } catch {
    return false;
  }
}

// ---------- Git remote URL parsing (TypeScript, for shell.env KEY=VALUE output) ----------

function parseGitHubUrl(url: string): { owner: string; repo: string } | null {
  // SSH: git@github.com:owner/repo.git
  const sshMatch = url.match(/^git@github\.com:([^/]+)\/([^/]+?)(?:\.git)?$/);
  if (sshMatch) {
    return { owner: sshMatch[1], repo: sshMatch[2] };
  }
  // HTTPS: https://github.com/owner/repo.git
  const httpsMatch = url.match(/^https:\/\/github\.com\/([^/]+)\/([^/]+?)(?:\.git)?$/);
  if (httpsMatch) {
    return { owner: httpsMatch[1], repo: httpsMatch[2] };
  }
  return null;
}

function parseGitBucketUrl(
  url: string,
  projectDir: string,
): { baseUrl: string | null; owner: string; repo: string; sshUrl: string | null } | null {
  let owner: string | null = null;
  let repo: string | null = null;

  // SSH with port: ssh://git@hostname:port/owner/repo.git
  const sshUrlMatch = url.match(/^ssh:\/\/git@([^:/]+):(\d+)\/([^/]+)\/([^/]+?)(?:\.git)?$/);
  if (sshUrlMatch) {
    owner = sshUrlMatch[3];
    repo = sshUrlMatch[4];
  }

  if (!owner) {
    // SSH short: git@hostname:owner/repo.git
    const sshShortMatch = url.match(/^git@([^:]+):([^/]+)\/([^/]+?)(?:\.git)?$/);
    if (sshShortMatch) {
      owner = sshShortMatch[2];
      repo = sshShortMatch[3];
    }
  }

  if (!owner) {
    // HTTPS: https://hostname/owner/repo.git
    const httpsMatch = url.match(/^https:\/\/([^/]+)\/([^/]+)\/([^/]+?)(?:\.git)?$/);
    if (httpsMatch) {
      owner = httpsMatch[2];
      repo = httpsMatch[3];
    }
  }

  if (!owner || !repo) {
    return null;
  }

  // Extract SSH base URL for GitBucket
  let sshUrl: string | null = null;
  const sshBaseMatch = url.match(/^(ssh:\/\/git@[^:/]+:\d+)/);
  if (sshBaseMatch) {
    sshUrl = sshBaseMatch[1];
  }

  // Base URL comes from .env, not from remote URL
  const baseUrl = readGitBucketUrlFromEnv(path.join(projectDir, ENV_FILE));

  return { baseUrl, owner, repo, sshUrl };
}

function readGitBucketUrlFromEnv(envPath: string): string | null {
  try {
    if (fs.existsSync(envPath)) {
      const content = fs.readFileSync(envPath, "utf8");
      let htmlUrl: string | null = null;
      let legacyUrl: string | null = null;
      for (const line of content.split("\n")) {
        const trimmed = line.trim();
        if (trimmed.startsWith("GITBUCKET_HTML_URL=")) {
          htmlUrl = trimmed.split("=", 2)[1].trim();
        } else if (trimmed.startsWith("GITBUCKET_URL=")) {
          legacyUrl = trimmed.split("=", 2)[1].trim();
        }
      }
      return htmlUrl || legacyUrl;
    }
  } catch {
    // Ignore read errors
  }
  return null;
}

export async function EnvLoaderPlugin(input: PluginInput): Promise<Hooks> {
  const projectDir = input?.directory || process.cwd();
  const envPath = path.join(projectDir, ENV_FILE);

  return {
    "shell.env": async (_input, output) => {
      // --- .env file values ---
      if (fs.existsSync(envPath)) {
        const content = fs.readFileSync(envPath, "utf8");
        const { env, warnings } = parseEnvFile(content);

        for (const [key, value] of Object.entries(env)) {
          output.env[key] = value;
        }

        // Flag non-gitignored .env
        if (!isEnvGitignored(projectDir)) {
          output.env["ENV_LOADER_SECURITY_WARNING"] =
            "SECURITY: .env file is NOT in .gitignore. Secrets may be committed to version control. Add '.env' to .gitignore immediately.";
          writeDiagnostic(projectDir, {
            source: "env-loader",
            level: "warning",
            message: ".env file is NOT in .gitignore — secrets may be committed to version control",
          });
        }

        if (warnings.length > 0) {
          console.error("[env-loader] " + warnings.join("; "));
          for (const w of warnings) {
            writeDiagnostic(projectDir, {
              source: "env-loader",
              level: "warning",
              message: w,
            });
          }
        }
      }

      // --- WORKTREE_PATH from PluginInput ---
      const worktreeDir = input?.worktree || "";
      const mainRepoDir = input?.directory || "";
      if (worktreeDir && worktreeDir !== mainRepoDir) {
        output.env["WORKTREE_PATH"] = worktreeDir;
      }

      // input.$ runs git commands in the session working directory (worktree when active)
      try {
        // Branch name
        const branchResult = await input.$.nothrow()`git branch --show-current`;
        if (branchResult.exitCode === 0) {
          const branch = branchResult.text().trim();
          if (branch) {
            output.env["BRANCH_NAME"] = branch;
          }
        }

        // Remote URL
        const remoteResult = await input.$.nothrow()`git remote get-url origin`;
        if (remoteResult.exitCode === 0) {
          const remoteUrl = remoteResult.text().trim();

          if (remoteUrl.includes("github.com")) {
            output.env["GIT_PLATFORM"] = "github";
            const parsed = parseGitHubUrl(remoteUrl);
            if (parsed) {
              output.env["GIT_OWNER"] = parsed.owner;
              output.env["GIT_REPO"] = parsed.repo;
            }
            output.env["GITHUB_HTML_URL"] = "https://github.com/";
          } else {
            output.env["GIT_PLATFORM"] = "gitbucket";
            const parsed = parseGitBucketUrl(remoteUrl, projectDir);
            if (parsed) {
              output.env["GIT_OWNER"] = parsed.owner;
              output.env["GIT_REPO"] = parsed.repo;
              if (parsed.baseUrl) {
                output.env["GITBUCKET_HTML_URL"] = parsed.baseUrl;
              }
              if (parsed.sshUrl) {
                output.env["GITBUCKET_SSH_URL"] = parsed.sshUrl;
              }
              // Check credentials from .env
              const hasToken = output.env["GITBUCKET_TOKEN"] && output.env["GITBUCKET_TOKEN"].length > 0;
              const hasUrl = output.env["GITBUCKET_HTML_URL"] || output.env["GITBUCKET_URL"];
              output.env["GITBUCKET_HAS_CREDENTIALS"] = (hasToken && hasUrl) ? "true" : "false";
            }
          }
        }

        // Git user config
        const nameResult = await input.$.nothrow()`git config user.name`;
        if (nameResult.exitCode === 0) {
          const name = nameResult.text().trim();
          if (name) {
            output.env["DEV_NAME"] = name;
          }
        }

        const emailResult = await input.$.nothrow()`git config user.email`;
        if (emailResult.exitCode === 0) {
          const email = emailResult.text().trim();
          if (email) {
            output.env["DEV_EMAIL"] = email;
          }
        }
      } catch {
        // Git commands unavailable — skip git env values
      }
    },
  };
}

export default EnvLoaderPlugin;
export { parseEnvFile, isEnvGitignored, writeDiagnostic, DIAGNOSTICS_PATH };
export type { PluginDiagnostic };
