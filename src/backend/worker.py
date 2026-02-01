# Copyright (c) 2026 Brothertown Language
# Note: Local development requires CORS handling for frontend (localhost:8501)
# and backend (localhost:8787) communication.
from js import Response, JSON, fetch, AbortSignal
import json
import sys
import time
# ------------------------------------------------------------
# Requests Shim (for environments without requests)
# ------------------------------------------------------------

class ResponseShim:
    def __init__(self, status_code, data, text=None):
        self.status_code = status_code
        self._data = data
        self.text = text or __import__('json').dumps(data)
    def json(self):
        return self._data
    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP Error {self.status_code}: {self.text}")

class RequestsShim:
    async def post(self, url, json=None, headers=None, data=None):
        fetch_options = {"method": "POST"}
        if headers:
            fetch_options["headers"] = headers
        if json is not None:
            if "headers" not in fetch_options:
                fetch_options["headers"] = {}
            fetch_options["headers"]["Content-Type"] = "application/json"
            fetch_options["body"] = JSON.stringify(JSON.parse(__import__('json').dumps(json)))
        elif data:
            fetch_options["body"] = data
            
        res = await fetch(url, JSON.parse(__import__('json').dumps(fetch_options)))
        status = res.status
        text = await res.text()
        try:
            return ResponseShim(status, __import__('json').loads(text), text)
        except:
            return ResponseShim(status, {}, text)

    async def get(self, url, headers=None):
        fetch_options = {"method": "GET"}
        if headers:
            fetch_options["headers"] = headers
        res = await fetch(url, JSON.parse(__import__('json').dumps(fetch_options)))
        status = res.status
        text = await res.text()
        try:
            return ResponseShim(status, __import__('json').loads(text), text)
        except:
            return ResponseShim(status, {}, text)

requests = RequestsShim()

from urllib.parse import urlencode, parse_qs
from mdf_parser import parse_mdf
import os
import base64
import hmac
import hashlib

# ------------------------------------------------------------
# Token signing helpers (no middleware)
# ------------------------------------------------------------

def sign_session(data: dict, secret: str) -> str:
    payload = json.dumps(data, separators=(",", ":")).encode()
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + sig).decode()

def verify_session(token: str, secret: str):
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        payload, sig = raw.rsplit(b".", 1)
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(payload.decode())
    except Exception:
        return None

# Small helpers
def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def _b64url_decode(s: str) -> bytes:
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def _hmac_sha256(key: str, msg: str) -> str:
    return _b64url(hmac.new(key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).digest())

# Global flag to ensure initialization happens once per worker instance
_initialized = False
# Counter to allow seeding to continue on subsequent requests if needed
_seeding_complete = False

async def initialize_db(db):
    global _initialized, _seeding_complete
    if _initialized and _seeding_complete:
        return
    
    # Ensure tables exist according to SCHEMA.md
    try:
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                citation_format TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """).run()
        
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                lx TEXT NOT NULL,
                ps TEXT,
                ge TEXT,
                mdf_data TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                source_page TEXT,
                current_version INTEGER NOT NULL DEFAULT 1,
                is_deleted INTEGER NOT NULL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT,
                reviewed_at DATETIME,
                reviewed_by TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        """).run()

        await db.prepare("""
            CREATE TABLE IF NOT EXISTS seeding_progress (
                source_name TEXT PRIMARY KEY,
                last_index INTEGER NOT NULL DEFAULT 0,
                total_records INTEGER NOT NULL DEFAULT 0,
                is_complete INTEGER NOT NULL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """).run()

        await db.prepare("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                github_id INTEGER UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                name TEXT,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """).run()

        await db.prepare("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                github_org TEXT NOT NULL,
                github_team TEXT,
                role TEXT NOT NULL DEFAULT 'viewer',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
            )
        """).run()
    except Exception as e:
        print(f"Error creating tables: {e}")

    # Check if sources exist
    try:
        sources_res = await db.prepare("SELECT count(*) as count FROM sources").first()
        if sources_res:
            count_data = sources_res.to_py()
            # Handle different possible return formats (dict or object with attribute)
            count = count_data.get('count') if isinstance(count_data, dict) else getattr(count_data, 'count', 0)
            if int(count) == 0:
                await db.prepare("INSERT INTO sources (name, description) VALUES (?, ?)").bind(
                    "Natick/Trumbull", "Natick Dictionary (Trumbull, 1903)"
                ).run()
        else:
            # If for some reason first() returns None but we expect a count
            await db.prepare("INSERT INTO sources (name, description) VALUES (?, ?)").bind(
                "Natick/Trumbull", "Natick Dictionary (Trumbull, 1903)"
            ).run()
    except Exception as e:
        print(f"Error checking sources: {e}")
    
    source_id = 1
    try:
        source_res = await db.prepare("SELECT id FROM sources WHERE name = ?").bind("Natick/Trumbull").first()
        if source_res:
            source_data = source_res.to_py()
            source_id = int(source_data.get('id') if isinstance(source_data, dict) else getattr(source_data, 'id', 1))
    except Exception as e:
        print(f"Error getting source_id: {e}")

    # Check if records exist
    try:
        progress_res = await db.prepare("SELECT * FROM seeding_progress WHERE source_name = ?").bind("Natick/Trumbull").first()
        progress = progress_res.to_py() if progress_res else None
        
        if not progress or int(progress['is_complete']) == 0:
            # Seed from file
            content = None
            import os
            base_dir = os.path.dirname(__file__)
            paths_to_try = [
                os.path.join(base_dir, "seed_data/natick.txt"),
                os.path.join(base_dir, "natick.txt"),
                "/session/metadata/seed_data/natick.txt",
                "seed_data/natick.txt",
                "natick.txt",
                "src/backend/seed_data/natick.txt"
            ]
            
            for path_to_try in paths_to_try:
                try:
                    with open(path_to_try, "r") as f:
                        content = f.read()
                    break
                except FileNotFoundError:
                    continue
            
            if content is None:
                raise FileNotFoundError("Could not find seed data file.")
            
            parsed = parse_mdf(content)
            total = len(parsed)
            
            start_index = int(progress['last_index']) if progress else 0
            
            if not progress:
                await db.prepare("INSERT INTO seeding_progress (source_name, total_records) VALUES (?, ?)").bind(
                    "Natick/Trumbull", total
                ).run()

            # Seed in smaller chunks to avoid hung code
            batch_size = 50
            max_batches_per_call = 100 # 5000 records per call
            
            batches_processed = 0
            for i in range(start_index, total, batch_size):
                if batches_processed >= max_batches_per_call:
                    break
                    
                end = min(i + batch_size, total)
                batch = parsed[i:end]
                statements = []
                for record in batch:
                    statements.append(
                        db.prepare(
                            "INSERT INTO records (source_id, lx, ps, ge, mdf_data, status) VALUES (?, ?, ?, ?, ?, ?)"
                        ).bind(source_id, record['lx'], record['ps'], record['ge'], record['mdf_data'], 'draft')
                    )
                if statements:
                    await db.batch(statements)
                
                batches_processed += 1
                new_index = end
                is_complete = 1 if new_index >= total else 0
                
                await db.prepare("UPDATE seeding_progress SET last_index = ?, is_complete = ?, updated_at = CURRENT_TIMESTAMP WHERE source_name = ?").bind(
                    new_index, is_complete, "Natick/Trumbull"
                ).run()
                
                if is_complete:
                    _seeding_complete = True
            
            if not _seeding_complete and progress and int(progress['is_complete']) == 1:
                _seeding_complete = True
                
    except Exception as e:
        print(f"Error seeding records: {e}")

    _initialized = True

async def on_fetch(request, env, ctx):
    url = request.url
    path = "/" + "/".join(url.split("/")[3:])
    
    # Frontend origin must be explicitly configured. Avoid host heuristics.
    # Allowed vars: SNEA_FRONTEND_URL (prod) or FRONTEND_URL (local). Final fallback: http://localhost:8501
    # Priority: Env var -> Heuristic for local dev
    frontend_url = getattr(env, "SNEA_FRONTEND_URL", getattr(env, "FRONTEND_URL", None))
    if not frontend_url:
        # Heuristic: If we are not on a production domain, assume local streamlit
        if "michael-conrad.com" not in url:
            frontend_url = "http://localhost:8501"
        else:
            frontend_url = "https://snea.michael-conrad.com" # Default prod frontend

    # CORS headers (allow configured frontend origin or *)
    allow_origin = frontend_url or "*"
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        # Allow AI debug header for local development tooling
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-AI-Debug",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin"
    }

    db = env.DB
    # One-time initialization per worker instance
    try:
        await initialize_db(db)
    except Exception as e:
        print(f"FAILED TO INITIALIZE DB: {e}")

    # Handle CORS preflight early
    if request.method == "OPTIONS":
        return Response.new("", headers=JSON.parse(json.dumps(headers)), status=204)

    # Require User-Agent on inbound requests as well (helps traceability)
    try:
        req_headers = dict(request.headers.to_py()) if hasattr(request.headers, "to_py") else {}
    except Exception:
        req_headers = {}
    inbound_ua = None
    for k, v in req_headers.items():
        if k.lower() == "user-agent":
            inbound_ua = v
            break
    if not inbound_ua:
        return Response.new(json.dumps({"error": "Missing User-Agent header"}), headers=JSON.parse(json.dumps(headers)), status=400)

    # -------- AI Debug (local dev) --------
    # Goal: Provide detailed, machine-readable diagnostics for the AI agent
    # without surfacing them in normal user experiences.
    # Enable when both conditions hold:
    #   1) Env AI_DEBUG is truthy ("1", "true")
    #   2) Request carries header X-AI-Debug: 1
    ai_debug_env = str(getattr(env, "AI_DEBUG", "0")).lower() in ("1", "true", "yes")
    ai_debug_header = any(k.lower() == "x-ai-debug" and str(v).strip() == "1" for k, v in req_headers.items())
    ai_debug_on = bool(ai_debug_env and ai_debug_header)

    def _dbg_events():
        # simple factory to isolate the mutable list
        return []

    def _dbg_add(events, kind, info):
        try:
            # Avoid leaking secrets; scrub common sensitive fields
            if isinstance(info, dict):
                info = {k: ("<redacted>" if k in {"client_secret", "access_token", "authorization"} else v) for k, v in info.items()}
            events.append({
                "t": int(__import__('time').time()*1000),
                "k": kind,
                "v": info,
            })
        except Exception:
            # Never let debug logging break the request
            pass

    def _with_debug(payload_dict, events):
        if not ai_debug_on:
            return payload_dict, headers
        # Clone headers and set a signal header
        dbg_headers = dict(headers)
        dbg_headers["X-AI-Debug"] = "1"
        try:
            payload = dict(payload_dict)
            payload["__ai_debug"] = events
            return payload, dbg_headers
        except Exception:
            return payload_dict, dbg_headers

    # Authentication temporarily disabled for protected routes; OAuth endpoints below
    is_authenticated = True
    
    # OAuth endpoints (GitHub)
    if path == "/api/oauth/login":
        dbg = _dbg_events() if ai_debug_on else None
        # Config
        client_id = getattr(env, "SNEA_GITHUB_CLIENT_ID", getattr(env, "GITHUB_CLIENT_ID", None))
        # Allow explicit override first
        override_redirect_base = getattr(env, "OAUTH_REDIRECT_BASE", None)
        # Prefer frontend URLs for redirect in local dev (frontend receives code then calls backend)
        frontend_redirect_base = getattr(env, "SNEA_FRONTEND_URL", getattr(env, "FRONTEND_URL", None))
        # Backend URLs (used if neither override nor frontend is provided)
        backend_redirect_base = getattr(env, "SNEA_BACKEND_URL", getattr(env, "BACKEND_URL", None))
        scope = getattr(env, "GITHUB_OAUTH_SCOPE", "read:user user:email")
        state_secret = getattr(env, "OAUTH_STATE_SECRET", getattr(env, "JWT_SECRET", "change-me"))
        
        try:
            if not client_id:
                return Response.new(json.dumps({"error": "GITHUB_CLIENT_ID not configured"}), headers=JSON.parse(json.dumps(headers)), status=500)

            # Compute redirect_uri
            # Priority: explicit override -> state-stored (if we had it) -> automatic discovery
            # We want to redirect back to where the user came from (frontend).
            
            # Priority 1: OAUTH_REDIRECT_BASE (explicit override)
            redirect_base = getattr(env, "OAUTH_REDIRECT_BASE", None)
            
            # Priority 2: Inferred from FRONTEND_URL
            if not redirect_base:
                redirect_base = frontend_url
                
            if redirect_base:
                # If redirecting to frontend, keep as-is. If to backend, append path.
                # Local dev: frontend is 8501, backend is 8787.
                is_frontend = "8501" in redirect_base or "snea.michael-conrad.com" in redirect_base
                if is_frontend:
                    redirect_uri = redirect_base.rstrip('/')
                else:
                    redirect_uri = redirect_base.rstrip('/') + "/api/oauth/callback"
            else:
                # Fallback to current origin (backend)
                parts = url.split('/')
                origin = parts[0] + '//' + parts[2] if len(parts) > 2 else ""
                redirect_uri = origin + "/api/oauth/callback"

            # Optional PKCE (per GitHub docs). When enabled, we add code_challenge to the
            # authorize URL and carry the code_verifier inside the signed state.
            use_pkce = str(getattr(env, "GITHUB_OAUTH_PKCE", getattr(env, "OAUTH_USE_PKCE", "0"))).lower() in ("1", "true", "yes")
            pkce_verifier = None
            pkce_challenge = None
            if use_pkce:
                # Generate a high-entropy code_verifier (43-128 chars). We'll use 48 bytes then base64url w/o padding.
                pkce_verifier = _b64url(os.urandom(64))
                # code_challenge = BASE64URL-ENCODE(SHA256(verifier)) without padding
                pkce_challenge = _b64url(hashlib.sha256(pkce_verifier.encode("utf-8")).digest())

            # Build state with HMAC for integrity. Carry nonce, timestamp, redirect_uri, and optional PKCE verifier.
            nonce = _b64url(os.urandom(16))
            state_obj = {"n": nonce, "t": int(__import__('time').time()), "r": redirect_uri}
            if pkce_verifier:
                # include the verifier so the backend can submit it in the token exchange
                state_obj["pkce_v"] = pkce_verifier
            state_payload = json.dumps(state_obj)
            sig = _hmac_sha256(state_secret, state_payload)
            state = _b64url(state_payload.encode("utf-8")) + "." + sig

            if dbg is not None:
                _dbg_add(dbg, "oauth.login.config", {
                    "override_redirect_base": override_redirect_base,
                    "frontend_redirect_base": frontend_redirect_base,
                    "backend_redirect_base": backend_redirect_base,
                    "redirect_uri": redirect_uri,
                    "scope": scope,
                })
                _dbg_add(dbg, "oauth.login.state", {
                    "nonce_len": len(nonce or ""),
                    "state_len": len(state or ""),
                })

            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "allow_signup": "false",
            }
            if pkce_challenge:
                params["code_challenge"] = pkce_challenge
                params["code_challenge_method"] = "S256"
            auth_url = "https://github.com/login/oauth/authorize?" + urlencode(params)
            # Echo redirect_uri for easier verification/debugging on the client side
            payload = {
                "authorize_url": auth_url,
                "state": state,
                "redirect_uri": redirect_uri,
                "pkce": True if use_pkce else False,
            }
            payload, out_headers = _with_debug(payload, dbg or [])
            return Response.new(json.dumps(payload), headers=JSON.parse(json.dumps(out_headers)))
        except Exception as e:
            err_data = {"error": str(e), "traceback": __import__('traceback').format_exc()}
            return Response.new(json.dumps(err_data), headers=JSON.parse(json.dumps(headers)), status=500)

    # Support POST /api/oauth/callback with JSON body {"code": ..., "state": ...}
    if path == "/api/oauth/callback" and request.method == "POST":
        dbg = _dbg_events() if ai_debug_on else None
        if dbg is not None:
            _dbg_add(dbg, "oauth.cb.start", {"python_version": sys.version, "path": path})
        
        try:
            body = await request.json()
            body_py = body.to_py() if hasattr(body, 'to_py') else body
        except Exception:
            body_py = {}

        code = body_py.get("code")
        state = body_py.get("state")
        if not code or not state:
            return Response.new(json.dumps({"error": "Missing code or state"}), headers=JSON.parse(json.dumps(headers)), status=400)

        client_id = getattr(env, "SNEA_GITHUB_CLIENT_ID", getattr(env, "GITHUB_CLIENT_ID", None))
        client_secret = getattr(env, "SNEA_GITHUB_CLIENT_SECRET", getattr(env, "GITHUB_CLIENT_SECRET", None))
        state_secret = getattr(env, "OAUTH_STATE_SECRET", getattr(env, "JWT_SECRET", "change-me"))
        
        if not client_id or not client_secret:
            return Response.new(json.dumps({"error": "GitHub OAuth not configured"}), headers=JSON.parse(json.dumps(headers)), status=500)

        # Verify state
        try:
            state_payload_b64, _, state_sig = state.partition('.')
            payload_bytes = _b64url_decode(state_payload_b64)
            expected_sig = _hmac_sha256(state_secret, payload_bytes.decode("utf-8"))
            if not hmac.compare_digest(state_sig, expected_sig):
                return Response.new(json.dumps({"error": "Invalid state"}), headers=JSON.parse(json.dumps(headers)), status=400)
            state_obj = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return Response.new(json.dumps({"error": "Invalid state"}), headers=JSON.parse(json.dumps(headers)), status=400)

        # Exchange code for access token
        token_url = "https://github.com/login/oauth/access_token"
        redirect_uri = state_obj.get("r")
        
        gh_payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        if state_obj.get("pkce_v"):
            gh_payload["code_verifier"] = state_obj.get("pkce_v")

        gh_headers = {"Accept": "application/json"}
        
        try:
            # Use requests-compatible API as requested
            token_res = await requests.post(
                token_url, 
                json=gh_payload, 
                headers=gh_headers
            )
            
            if token_res.status_code != 200:
                return Response.new(json.dumps({"error": "GitHub token exchange failed", "status": token_res.status_code}), headers=JSON.parse(json.dumps(headers)), status=502)
            
            token_data = token_res.json()
        except Exception as e:
            return Response.new(json.dumps({"error": f"Token exchange failed: {e}"}), headers=JSON.parse(json.dumps(headers)), status=502)

        access_token = token_data.get("access_token")
        if not access_token:
            return Response.new(json.dumps({"error": "No access_token from GitHub", "details": token_data}), headers=JSON.parse(json.dumps(headers)), status=502)

        # Fetch user info using requests for simplicity
        try:
            api_headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": getattr(env, "GITHUB_USER_AGENT", "python-worker"),
                "X-GitHub-Api-Version": "2022-11-28"
            }
            user_res = await requests.get("https://api.github.com/user", headers=api_headers)
            user_res.raise_for_status()
            uj = user_res.json()
            
            # Email fetch is optional but helpful
            email = uj.get("email")
            if not email:
                try:
                    email_res = await requests.get("https://api.github.com/user/emails", headers=api_headers)
                    ej = email_res.json() if email_res.status_code == 200 else []
                    if isinstance(ej, list):
                        primary = next((x for x in ej if x.get("primary")), None)
                        email = (primary or (ej[0] if ej else {})).get("email")
                except Exception:
                    pass
        except Exception as e:
            return Response.new(json.dumps({"error": f"GitHub API failed: {e}"}), headers=JSON.parse(json.dumps(headers)), status=502)

        # Extract fields
        github_id = uj.get("id")
        username = uj.get("login")
        name = uj.get("name")
        
        if not (github_id and username):
            return Response.new(json.dumps({"error": "Incomplete GitHub profile"}), headers=JSON.parse(json.dumps(headers)), status=502)

        # Upsert user and create session
        try:
            existing = await db.prepare("SELECT id FROM users WHERE github_id = ?").bind(github_id).first()
            if existing:
                await db.prepare("UPDATE users SET email = ?, username = ?, name = ?, last_login = CURRENT_TIMESTAMP WHERE github_id = ?").bind(email, username, name, github_id).run()
                user_id = int((existing.to_py() or {}).get("id", 0))
            else:
                await db.prepare("INSERT INTO users (email, github_id, username, name, last_login) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)").bind(email, github_id, username, name).run()
                new_row = await db.prepare("SELECT id FROM users WHERE github_id = ?").bind(github_id).first()
                user_id = int((new_row.to_py() or {}).get("id", 0))
            
            session_secret = getattr(env, "SESSION_SECRET", getattr(env, "JWT_SECRET", "change-me"))
            session_payload = {
                "uid": user_id, 
                "gh": github_id, 
                "u": username, 
                "iat": int(time.time())
            }
            
            signed_session = sign_session(session_payload, session_secret)
            
            # Use the Response.new to set headers including Set-Cookie
            out_headers = dict(headers)
            out_headers["Set-Cookie"] = (
                f"session={signed_session}; "
                "HttpOnly; Secure; SameSite=Lax; Path=/"
            )
            
            success_payload = {
                "token": signed_session, # keep for backward compatibility with frontend
                "user": {"id": user_id, "email": email, "username": username, "name": name}
            }
            return Response.new(json.dumps(success_payload), headers=JSON.parse(json.dumps(out_headers)))
        except Exception as e:
            return Response.new(json.dumps({"error": f"DB or Session error: {e}"}), headers=JSON.parse(json.dumps(headers)), status=500)

    # Protected routes
    if path.startswith("/api/") and path not in ["/api/oauth/login", "/api/oauth/callback", "/api/health"]:
        # Verify session via cookie or Authorization header
        cookie_header = req_headers.get("cookie", "")
        token = None
        for part in cookie_header.split(";"):
            if part.strip().startswith("session="):
                token = part.strip().split("=", 1)[1]
        
        if not token:
            auth_header = req_headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return Response.new(json.dumps({"error": "Unauthorized"}), headers=JSON.parse(json.dumps(headers)), status=401)

        session_secret = getattr(env, "SESSION_SECRET", getattr(env, "JWT_SECRET", "change-me"))
        session = verify_session(token, session_secret)
        if not session:
            return Response.new(json.dumps({"error": "Invalid session"}), headers=JSON.parse(json.dumps(headers)), status=401)
        
        # Attach session to context for downstream handlers if needed
        # (Since we are in a single function, we'll just use the 'session' variable)
    
    if path == "/api/records/count":
        try:
            res = await db.prepare("SELECT count(*) as count FROM records").first()
            count_val = 0
            if res:
                if hasattr(res, "to_py"):
                    rp = res.to_py()
                    count_val = int(rp.get("count", 0))
                else:
                    count_val = int(getattr(res, "count", 0))
            data = {"count": count_val}
        except Exception as e:
            data = {"error": str(e)}
        return Response.new(json.dumps(data), headers=JSON.parse(json.dumps(headers)))

    if path == "/api/records":
        try:
            # Join with sources to get source name
            records = await db.prepare("""
                SELECT r.*, s.name as source_name 
                FROM records r 
                LEFT JOIN sources s ON r.source_id = s.id 
                WHERE r.is_deleted = 0 
                ORDER BY r.lx ASC 
                LIMIT 100
            """).all()
            # Convert results to list of dicts for JSON serialization
            data = [dict(r.to_py()) for r in records.results]
        except Exception as e:
            data = {"error": str(e)}
            
        return Response.new(json.dumps(data), headers=JSON.parse(json.dumps(headers)))

    if path.startswith("/api/records/") and request.method == "POST":
        # Record update endpoint: /api/records/<id>
        try:
            record_id = int(path.split("/")[-1])
            body = await request.json()
            body_py = body.to_py() if hasattr(body, 'to_py') else body
            
            lx = body_py.get("lx")
            ps = body_py.get("ps")
            ge = body_py.get("ge")
            mdf_data = body_py.get("mdf_data")
            
            if not lx:
                return Response.new(json.dumps({"error": "lx is required"}), headers=JSON.parse(json.dumps(headers)), status=400)
            
            # Update record
            await db.prepare("""
                UPDATE records 
                SET lx = ?, ps = ?, ge = ?, mdf_data = ?, updated_at = CURRENT_TIMESTAMP, updated_by = ?, current_version = current_version + 1
                WHERE id = ?
            """).bind(lx, ps, ge, mdf_data, session.get("u"), record_id).run()
            
            return Response.new(json.dumps({"success": True}), headers=JSON.parse(json.dumps(headers)))
        except Exception as e:
            return Response.new(json.dumps({"error": str(e)}), headers=JSON.parse(json.dumps(headers)), status=500)

    if path == "/api/dev/info":
        try:
            tables = await db.prepare("SELECT name, sql FROM sqlite_master WHERE type='table'").all()
            table_list = [dict(r.to_py()) for r in tables.results]
            
            progress = await db.prepare("SELECT * FROM seeding_progress").all()
            progress_list = [dict(r.to_py()) for r in progress.results]
        except Exception as e:
            table_list = [{"error": str(e)}]
            progress_list = []

        data = {
            "python_version": sys.version,
            "platform": sys.platform,
            "tables": table_list,
            "seeding_progress": progress_list
        }
        return Response.new(json.dumps(data), headers=JSON.parse(json.dumps(headers)))

    # Removed /api/dev/auth-logs endpoints as part of OAuth backend removal

    if path == "/api/health":
        return Response.new(json.dumps({"ok": True}), headers=JSON.parse(json.dumps(headers)))

    if path == "/api/me":
        cookie_header = req_headers.get("cookie", "")
        token = None
        for part in cookie_header.split(";"):
            if part.strip().startswith("session="):
                token = part.strip().split("=", 1)[1]

        if not token:
            return Response.new(json.dumps({"error": "Unauthorized"}), headers=JSON.parse(json.dumps(headers)), status=401)

        session_secret = getattr(env, "SESSION_SECRET", getattr(env, "JWT_SECRET", "change-me"))
        session = verify_session(token, session_secret)
        if not session:
            return Response.new(json.dumps({"error": "Invalid session"}), headers=JSON.parse(json.dumps(headers)), status=401)

        return Response.new(json.dumps({
            "user_id": session.get("uid"),
            "login": session.get("u")
        }), headers=JSON.parse(json.dumps(headers)))

    # Default 404 JSON to avoid JSON parsing errors on clients hitting wrong path
    return Response.new(json.dumps({"error": "Not found", "path": path}), headers=JSON.parse(json.dumps(headers)), status=404)
