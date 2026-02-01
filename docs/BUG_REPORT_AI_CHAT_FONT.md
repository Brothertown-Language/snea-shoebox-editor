<!-- Copyright (c) 2026 Brothertown Language -->
# Bug Report: AI Chat Window Font Size Issue

### Summary
The font size in the AI chat interface is significantly smaller than the rest of the IDE (terminals, editor, settings dialogs) and does not respond correctly to standard scaling or zoom commands.

### Environment Details
- **IDE**: JetBrains (e.g., PyCharm, IntelliJ IDEA, etc.)
- **Component**: AI Assistant / Chat Window
- **Operating System**: Linux (based on path `/home/muksihs/...`)
- **Reported Date**: 2026-01-31

### Description
The AI chat window displays text at a much smaller scale compared to other UI elements. Even when global IDE appearance settings are adjusted or "use custom font" sizes are increased to the maximum, the text within the AI chat remains difficult to read.

### Observed Behavior
1.  Terminals and Editor windows respect font size settings.
2.  Settings dialog previews look correct.
3.  Standard Zoom (`Ctrl + +`) does not affect the AI chat window or does not scale the font effectively.
4.  The font size in the AI chat remains "hyper small" even when other IDE fonts are set to maximum.

### Steps Taken to Resolve (Unsuccessful)
1.  Adjusted **Appearance & Behavior > Appearance > Use custom font** to maximum.
2.  Adjusted **Editor > Color Scheme > Console Font**.
3.  Attempted browser/IDE zoom.

### Requested Fix
Ensure the AI chat window inherits global font size settings or provides a dedicated, functional font size control that matches the behavior of other IDE tool windows.
