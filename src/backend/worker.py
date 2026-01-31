# Copyright (c) 2026 Brothertown Language
# Note: Local development requires CORS handling for frontend (localhost:8765)
# and backend (localhost:8787) communication.
from js import Response, JSON, sys
import json

async def on_fetch(request, env, ctx):
    url = request.url
    path = "/" + "/".join(url.split("/")[3:])
    
    # Simple routing
    if path == "/api/dev/info":
        db = env.DB
        # Query table schemas
        try:
            tables = await db.prepare("SELECT name, sql FROM sqlite_master WHERE type='table'").all()
            # tables is a Result object, might need to convert to list/dict
            # Assuming Cloudflare D1 Python API (Beta)
            table_list = tables.results
        except Exception as e:
            table_list = [{"error": str(e)}]

        data = {
            "python_version": sys.version,
            "tables": table_list,
            "platform": sys.platform
        }
        
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # Required for local dev
        }
        return Response.new(json.dumps(data), headers=headers)

    return Response.new("SNEA Shoebox Backend")
