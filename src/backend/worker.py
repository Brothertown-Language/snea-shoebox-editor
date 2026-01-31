# Copyright (c) 2026 Brothertown Language
from js import Response

async def on_fetch(request, env, ctx):
    return Response.new("SNEA Shoebox Backend")
