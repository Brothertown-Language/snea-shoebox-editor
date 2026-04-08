import type { Hooks, PluginInput } from "@opencode-ai/plugin";

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
      console.error("[session-init] Script returned empty output");
      return { output: "", env: {} };
    }

    if (result.exitCode !== 0) {
      const stderr = result.stderr.toString();
      console.error(`[session-init] Script exited with code ${result.exitCode}: ${stderr}`);
      return { output: "", env: {} };
    }

    const env = parseEnvFromOutput(stdout);

    cachedOutput = stdout;
    cachedEnv = env;
    cacheTimestamp = Date.now();

    return { output: stdout, env };
  } catch (err) {
    console.error("[session-init] Failed to run session_init.py:", err);
    return { output: "", env: {} };
  }
}

export default async function sessionInitPlugin(input: PluginInput): Promise<Hooks> {
  return {
    "experimental.chat.system.transform": async (_input, output) => {
      const { output: scriptOutput } = await runSessionInit(input.$);
      if (scriptOutput) {
        output.system.push(scriptOutput);
      }
    },

    "shell.env": async (_input, output) => {
      const { env } = await runSessionInit(input.$);
      for (const [key, value] of Object.entries(env)) {
        output.env[key] = value;
      }
    },
  };
}