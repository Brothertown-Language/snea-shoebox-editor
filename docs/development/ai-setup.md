<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# AI Integration Guide (Ollama + Qwen)

This guide explains how to configure PyCharm to use the local Ollama instance running the **Qwen2.5-Coder-14B** model as your primary LLM backend.

## 1. Start the Model
Before configuring PyCharm, ensure the model is running. You can use the provided startup script:

```bash
./scripts/start_ollama_qwen.sh
```

Or run the **"Ollama Qwen"** run configuration directly from PyCharm's top menu.

## 2. Native Configuration (Recommended)

Since you are using **PyCharm Professional** with an **AI Assistant Subscription**, you can use the native integration. In Build #253, this is handled via the **Custom Models** section using the OpenAI-compatible protocol.

1.  Open **File | Settings** (`Ctrl+Alt+S`).
2.  Navigate to **Tools | AI Assistant | Custom Models** (this is a sub-node in the left-hand tree).
3.  Click the **Add Custom Model** button (or the **+** icon).
4.  In the **Provider** dropdown, select **OpenAI-compatible**.
5.  Set the **Model Name**: `qwen2.5-coder:14b`.
6.  Set the **Server URL**: `http://localhost:11434/v1` (Note the `/v1` suffix).
7.  Leave the **API Key** empty (Ollama doesn't require one locally).
8.  Click **OK**.
9.  Now, go back to the main **Tools | AI Assistant** page and ensure your new custom model is selected in the **Language Model** dropdown.

## 3. Alternative Plugin Options

If you prefer a sidebar-centric chat experience or need features not yet in the native assistant:

### Option A: Ollama Plugin (Lightweight)
1.  **Install**: `File | Settings | Plugins` > Search for **"Ollama"** (by Yuriy Artamonov).
2.  **Configure**: `File | Settings | Tools | Ollama`.
3.  **Server URL**: `http://localhost:11434`.

### Option B: Continue Plugin
1.  **Install**: `File | Settings | Plugins` > Search for **"Continue"**.
2.  **Open Config**: Click the **Continue icon** in the right-side sidebar and click the **gear icon**.
3.  **Edit `config.json`**:
    ```json
    {
      "models": [
        {
          "title": "Ollama Qwen 14B",
          "provider": "ollama",
          "model": "qwen2.5-coder:14b"
        }
      ]
    }
    ```

## 4. How to Use AI in PyCharm (Linux Shortcuts)

Once configured, you can interact with **Qwen 14B** through these primary methods:

### A. AI Chat (Sidebar)
- **What**: A persistent chat window for general questions or large code generation.
- **How**: Click the **AI Assistant** icon in the right-side tool window bar.
- **Tip**: Ensure `qwen2.5-coder:14b` is selected in the dropdown at the top of the chat window.

### B. Inline Code Generation & Editing
- **What**: Generate new code or modify existing lines directly in the editor.
- **How**: Press `Ctrl + \` (Standard Linux shortcut).
- **Usage**: Type a prompt like "create a function to parse MDF records" and press Enter.

### C. Contextual Actions (Right-Click)
- **What**: Explain, refactor, or find bugs in specific code blocks.
- **How**: Highlight a block of code, **Right-Click**, and select **AI Actions**.
- **Quick Explain**: Highlight code and press `Alt + Enter` -> **Explain Code**.

### D. Writing Documentation / Unit Tests
- **How**: Right-click a function name -> **AI Actions** -> **Write Documentation** or **Generate Unit Tests**.

## 5. Environment Summary
- **Model Name**: `qwen2.5-coder:14b`
- **Ollama Endpoint**: `http://localhost:11434`
- **VRAM Required**: ~9.0 GB (Fits well in RTX 3090/24GB).
