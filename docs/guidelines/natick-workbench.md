# Plan: Natick Workbench Desktop Application (PyQt6)

## 1. Objective
Create a native desktop application for the Brothertown Language Development Project to facilitate side-by-side comparison, search, and validation of Natick Dictionary records during the transformation process. This replaces the Streamlit-based utility with a more responsive and robust native interface.

## 2. Technical Architecture
- **Framework:** PyQt6 (Python bindings for Qt 6).
- **Environment:** Managed via `uv`.
- **Pattern:** Model-View-Controller (MVC).
    - **Model:** `NatickRecord` and `NatickProcessor` classes (existing logic).
    - **View:** `NatickWorkbenchWindow` (PyQt6 QMainWindow).
    - **Controller:** Signal/Slot handling for navigation, search, and validation.

## 3. Key Features
- **Side-by-Side Synchronized View:** Two `QPlainTextEdit` widgets with synchronized scrollbars.
- **Record Navigation:**
    - "Next" / "Previous" buttons.
    - "Jump to Index" input.
    - Record slider for fast scrubbing.
- **Search & Filter:**
    - Real-time search across original and processed text.
    - Filter by "Changed Only" (highlighting records where transformation occurred).
- **MDF Validation:**
    - Integrated check against `documentation/MDFields19a_UTF8.txt`.
    - Visual indicators (colors/icons) for records that fail validation.
- **Zero-Install Deployment:**
    - Uses `uv` to manage `PyQt6` binary wheels.
    - No system-level Qt installation required.

## 4. Implementation Phases

### Phase 1: Environment & Boilerplate
1. Add `PyQt6` to `pyproject.toml` dependencies.
2. Create `scripts/natick/natick_workbench.py` with basic window structure.
3. Implement self-contained asset loading (icons/styles).

### Phase 2: Data Integration
1. Adapt `parse_records` logic from `process_natick_records.py` for efficient GUI loading.
2. Implement background loading for the ~3,500 records to keep UI responsive.
3. Create a `RecordModel` to manage state between the two files.

### Phase 3: UI Implementation
1. Layout: Sidebar (Search/Nav) + Central Area (Side-by-Side Text).
2. Synchronize scrolling between left (Original) and right (Processed) panes.
3. Add syntax highlighting for MDF tags (`\lx`, `\ge`, etc.).

### Phase 4: Validation & Search
1. Implement the search engine (regex and literal).
2. Add real-time MDF compliance checking.
3. Create a "Jump to Error" feature.

## 5. Verification Plan
1. **Launch Test:** Verify `./launch_natick_workbench` opens on Linux (GNOME/KDE).
2. **Performance Test:** Verify smooth scrolling and <100ms search latency on the full dataset.
3. **Accuracy Test:** Compare record alignment with existing `compare_records_app.py` output.

## 6. Execution Command
```bash
./launch_natick_workbench.sh
```
