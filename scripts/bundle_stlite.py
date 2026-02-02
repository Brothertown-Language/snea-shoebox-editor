# Copyright (c) 2026 Brothertown Language
import os
import json
import shutil
from pathlib import Path

def bundle():
    """
    Fresh start for Stlite bundling.
    Generates a clean dist/index.html that mounts app.py.
    """
    print("Initializing fresh Stlite bundle...")
    
    root_dir = Path(__file__).parent.parent
    src_app = root_dir / "src" / "frontend" / "app.py"
    dist_dir = root_dir / "dist"
    
    if not src_app.exists():
        print(f"Error: {src_app} not found.")
        return

    with open(src_app, "r") as f:
        app_code = f.read()

    # Clean dist directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Requirements for Pyodide
    requirements = ["httpx", "python-dotenv"]
    STLITE_VERSION = "0.76.0"

    # Robust Template
    index_html = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>SNEA Shoebox Editor</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@{STLITE_VERSION}/build/stlite.css" />
    <style>
      #stlite:empty {{ display: none; }}
      #loader {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #f8f9fa;
        color: #343a40;
      }}
    </style>
  </head>
  <body>
    <div id="loader">
      <div style="text-align: center;">
        <div style="font-size: 1.2rem; margin-bottom: 1rem;">Initializing SNEA Editor...</div>
        <div style="font-size: 0.9rem; color: #6c757d;">Loading WebAssembly runtime and dependencies</div>
      </div>
    </div>
    <div id="stlite"></div>
    
    <!-- Hidden Python Source -->
    <script id="python-src" type="text/plain">{app_code}</script>

    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@{STLITE_VERSION}/build/stlite.js"></script>
    <script>
      (function() {{
        const code = document.getElementById("python-src").textContent;
        const requirements = {json.dumps(requirements)};
        
        if (typeof stlite === 'undefined') {{
          document.getElementById("loader").innerHTML = "Error: Failed to load Stlite library.";
          return;
        }}

        stlite.mount({{
          requirements: requirements,
          entrypoint: "app.py",
          files: {{
            "app.py": code
          }},
          streamlitConfig: {{
            "server.address": "0.0.0.0",
            "server.port": 8501,
            "browser.gatherUsageStats": false
          }}
        }}, document.getElementById("stlite")).then(() => {{
          document.getElementById("loader").style.display = "none";
          document.getElementById("stlite").style.display = "block";
        }}).catch(err => {{
          console.error("Stlite Mount Error:", err);
          document.getElementById("loader").innerHTML = "Error initializing app: " + err.message;
        }});
      }})();
    </script>
  </body>
</html>
"""
    with open(dist_dir / "index.html", "w") as f:
        f.write(index_html)
    
    print(f"Bundle complete: {dist_dir}/index.html")

if __name__ == "__main__":
    bundle()
