# Launcher Management for AI Agents

## Overview
This project uses PyCharm Run Configurations to manage the development environment. These configurations are stored in two locations that **MUST** be kept in sync:

1.  `launchers/`: The source-controlled directory for shared run configurations.
2.  `.idea/runConfigurations/`: The local IDE directory where PyCharm looks for configurations.

## Available Launchers

### 1. Streamlit (`Streamlit.xml`)
- **Type:** Shell Script (`ShConfigurationType`)
- **Script:** `scripts/start_streamlit.sh`
- **Purpose:** Starts the Streamlit frontend in the background using `nohup`.
- **Behavior:** Returns control to the IDE immediately while Streamlit continues to run.
- **Dependencies:** Automatically runs "Kill Streamlit" before starting to ensure a clean restart.

### 2. Kill Streamlit (`Kill_Streamlit.xml`)
- **Type:** Shell Script (`ShConfigurationType`)
- **Script:** `scripts/kill_streamlit.sh`
- **Purpose:** Identifies and terminates any running Streamlit processes associated with this project.
- **Usage:** Primarily used as a "Before Launch" task for the Streamlit launcher.

## AI Agent Guidelines
All operational instructions for AI agents have been consolidated in the `.junie/` directory. AI agents **MUST** review the guidelines in `.junie/ai-behavior.md` and related files at the start of every session.
