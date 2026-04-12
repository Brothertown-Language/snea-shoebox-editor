/**
 * Env-Loader Plugin for OpenCode
 *
 * Reads the project root `.env` file and injects all key-value pairs
 * into every shell session via the `shell.env` hook. Also flags to
 * the AI agent if `.env` is not gitignored, since that would be a
 * security breach (secrets committed to version control).
 *
 * Co-authored with AI: OpenCode (ollama-cloud/glm-5)
 */

import type { Hooks, PluginInput } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

const ENV_FILE = ".env";

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

export async function EnvLoaderPlugin(input: PluginInput): Promise<Hooks> {
  const projectDir = input?.directory || process.cwd();
  const envPath = path.join(projectDir, ENV_FILE);

  return {
    "shell.env": async (_input, output) => {
      if (!fs.existsSync(envPath)) {
        return;
      }

      const content = fs.readFileSync(envPath, "utf8");
      const { env, warnings } = parseEnvFile(content);

      for (const [key, value] of Object.entries(env)) {
        output.env[key] = value;
      }

      // Flag non-gitignored .env as a potential security breach
      if (!isEnvGitignored(projectDir)) {
        output.env["ENV_LOADER_SECURITY_WARNING"] =
          "SECURITY: .env file is NOT in .gitignore. Secrets may be committed to version control. Add '.env' to .gitignore immediately.";
      }

      if (warnings.length > 0) {
        console.error("[env-loader] " + warnings.join("; "));
      }
    },
  };
}

export default EnvLoaderPlugin;
export { parseEnvFile, isEnvGitignored };