# Copyright (c) 2026 Brothertown Language
import solara
import sys
import httpx
import json

# Reactive state for dev info
dev_info_state = solara.reactive(None)
error_state = solara.reactive(None)

async def fetch_dev_info():
    try:
        # Backend is on port 8787 in local dev
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8787/api/dev/info")
            if response.status_code == 200:
                dev_info_state.value = response.json()
            else:
                error_state.value = f"Error fetching dev info: {response.status_code}"
    except Exception as e:
        error_state.value = f"Exception during fetch: {str(e)}"

@solara.component
def DevInfo():
    # Trigger fetch on mount
    solara.use_task(fetch_dev_info, dependencies=[])

    with solara.Card("Developer Information"):
        with solara.Column():
            solara.Markdown(f"**Frontend Python Version:** `{sys.version}`")
            
            if error_state.value:
                solara.Error(error_state.value)
            
            if dev_info_state.value:
                solara.Markdown(f"**Backend Python Version:** `{dev_info_state.value.get('python_version')}`")
                solara.Markdown(f"**Backend Platform:** `{dev_info_state.value.get('platform')}`")
                
                solara.Markdown("### Database Tables (D1)")
                tables = dev_info_state.value.get("tables", [])
                if tables:
                    for table in tables:
                        if "name" in table:
                            with solara.Details(table["name"]):
                                solara.Preformatted(table.get("sql", "No SQL available"))
                else:
                    solara.Warning("No tables found or error querying database.")
            else:
                if not error_state.value:
                    solara.ProgressLinear(True)
                    solara.Info("Fetching data from backend...")

@solara.component
def Page():
    with solara.Column():
        solara.Title("SNEA Shoebox Editor")
        solara.Markdown("# SNEA Online Shoebox Editor")
        
        with solara.Sidebar():
            solara.Markdown("## Navigation")
            # solara.Link or similar for navigation if we had multiple pages
        
        with solara.Tabs():
            with solara.Tab("Editor"):
                solara.Info("Welcome to the concurrent editor for SNEA linguistic records.")
            with solara.Tab("Dev Info"):
                DevInfo()

@solara.component
def Layout(children):
    return solara.AppLayout(children=children)
