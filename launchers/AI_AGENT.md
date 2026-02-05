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

## AI Agent Instructions

### Synchronization Requirement
Whenever you modify a launcher in one location, you **MUST** immediately apply the exact same changes to the corresponding file in the other location.

- If you edit `launchers/X.xml`, you must edit `.idea/runConfigurations/X.xml`.
- If you edit `.idea/runConfigurations/X.xml`, you must edit `launchers/X.xml`.

### Background Execution
All Streamlit-related launchers must support background execution. Do **NOT** revert the Streamlit launcher to a standard `PythonConfigurationType` unless explicitly instructed, as this blocks the IDE's execution state. Always use the shell script wrappers (`scripts/start_streamlit.sh`).

### Commit Messages
When updating launchers, provide clear descriptions of the changes in your commit message. Do **NOT** use prefixes like `feat:` or `fix:`.
