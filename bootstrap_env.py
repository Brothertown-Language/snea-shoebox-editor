import os
import secrets

from cloudflare import Cloudflare
from github import Github, Auth
from nacl import encoding, public
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
ORG_NAME = os.getenv("ORG_NAME", "Brothertown-Language")
REPO_NAME = os.getenv("REPO_NAME", "snea-shoebox-editor")
BACKEND_NAME = os.getenv("BACKEND_NAME", "snea-backend")
PAGES_NAME = os.getenv("PAGES_NAME", "snea-editor")
DB_NAME = os.getenv("DB_NAME", "snea-shoebox")


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return encoding.Base64Encoder.encode(encrypted).decode("utf-8")


def bootstrap():
    # Cloudflare Initialization: Prefer User API Token for all operations
    cf_email = os.getenv("PROD_CF_EMAIL")
    cf_key = os.getenv("PROD_CF_API_KEY")
    cf_token = os.getenv("PROD_CF_API_TOKEN")

    if cf_token:
        print("Initializing Cloudflare client with User API Token...")
        cf = Cloudflare(api_token=cf_token)
        # Verify token works for listing accounts
        try:
            cf.accounts.list(page=1, per_page=1)
        except Exception as e:
            print(f"Token verification failed: {e}")
            if cf_email and cf_key:
                print("Falling back to Global API Key...")
                cf = Cloudflare(api_email=cf_email, api_key=cf_key)
            else:
                raise
    elif cf_email and cf_key:
        print("Initializing Cloudflare client with Global API Key...")
        cf = Cloudflare(api_email=cf_email, api_key=cf_key)
    else:
        raise Exception("Missing Cloudflare credentials. Provide PROD_CF_API_TOKEN (Recommended) or PROD_CF_EMAIL and PROD_CF_API_KEY in .env")

    gh_token = os.getenv("PROD_GH_TOKEN")
    if not gh_token:
        raise Exception("Missing GitHub token. Provide PROD_GH_TOKEN in .env")
        
    auth = Auth.Token(gh_token)
    gh = Github(auth=auth)

    # 0. Get Repository from Organization
    print(f"Connecting to organization: {ORG_NAME}...")
    org = gh.get_organization(ORG_NAME)
    repo = org.get_repo(REPO_NAME)

    # 1. Verification and Creation of D1 Database
    print(f"Verifying Cloudflare D1 database: {DB_NAME}...")
    accounts = list(cf.accounts.list())
    if not accounts:
        raise Exception("No Cloudflare accounts found. Ensure your CF_API_TOKEN has 'Account Settings: Read' permission.")
    
    account_id = accounts[0].id
    print(f"Using Cloudflare Account: {accounts[0].name} (ID: {account_id})")
    
    db = None
    try:
        print("Pre-check: Searching for existing D1 database...")
        existing_dbs = list(cf.d1.database.list(account_id=account_id))
        
        for edb in existing_dbs:
            if edb.name == DB_NAME:
                db_id = getattr(edb, "uuid", None) or getattr(edb, "id", None)
                print(f"SUCCESS: Database '{DB_NAME}' already exists (ID: {db_id}).")
                db = edb
                break
        
        if not db:
            print(f"Database '{DB_NAME}' not found. Creating it now...")
            db = cf.d1.database.create(account_id=account_id, name=DB_NAME)
            
            # Post-check: Verify creation
            db_id = getattr(db, "uuid", None) or getattr(db, "id", None)
            if db_id:
                print(f"SUCCESS: Database '{DB_NAME}' created successfully (ID: {db_id}).")
            else:
                raise Exception(f"FAILED: Database creation returned an invalid object: {db}")
                
    except Exception as e:
        print(f"Error during D1 verification/creation: {e}")
        raise
    
    # Final ID extraction for wrangler.toml
    db_id = getattr(db, "uuid", None) or getattr(db, "id", None)
    if not db_id:
        db_id = str(db)
        
    print(f"D1 Infrastructure Verified! Database ID: {db_id}")

    # 3. Handle Secrets
    # JWT_SECRET: Use from .env if available, otherwise generate
    jwt_secret = os.getenv("PROD_JWT_SECRET")
    generated_jwt = False
    if not jwt_secret:
        print("PROD_JWT_SECRET not found in .env. Generating a new one...")
        jwt_secret = secrets.token_urlsafe(32)
        generated_jwt = True

    # 4. Upload Secrets to GitHub
    public_key = repo.get_public_key()
    
    github_client_id = os.environ.get("PROD_SNEA_GITHUB_CLIENT_ID")
    github_client_secret = os.environ.get("PROD_SNEA_GITHUB_CLIENT_SECRET")
    
    secrets_to_upload = {
        "CLOUDFLARE_API_TOKEN": cf_token,
        "CLOUDFLARE_ACCOUNT_ID": account_id,
        "JWT_SECRET": jwt_secret,
        "SNEA_GITHUB_CLIENT_ID": github_client_id,
        "SNEA_GITHUB_CLIENT_SECRET": github_client_secret,
    }

    uploaded_secrets = []
    for name, value in secrets_to_upload.items():
        if value:
            print(f"Uploading secret {name}...")
            repo.create_secret(name, encrypt(public_key.key, value))
            uploaded_secrets.append(name)
        else:
            print(f"Skipping secret {name} (not found in .env)")

    # 4.1 Verify Secrets on GitHub
    print("\nVerifying GitHub secrets...")
    existing_secrets = [s.name for s in repo.get_secrets()]
    all_verified = True
    for name in uploaded_secrets:
        if name in existing_secrets:
            print(f"VERIFIED: Secret '{name}' is present on GitHub.")
        else:
            print(f"FAILED: Secret '{name}' NOT found on GitHub after upload.")
            all_verified = False
    
    if not all_verified:
        print("WARNING: Some secrets failed verification. Check GitHub repository settings.")

    # 5. Generate wrangler.backend.toml
    print(f"\nGenerating wrangler.backend.toml for '{BACKEND_NAME}'...")
    wrangler_content = f"""name = "{BACKEND_NAME}"
main = "src/backend/worker.py"
compatibility_date = "2024-01-01"
compatibility_flags = ["python_workers"] # MANDATORY: Required for Python Workers

[vars]
BACKEND_URL = "https://snea-backend.brothertownlanguage.org"

[build]
command = "uv pip install -e . && uv sync --all-groups"

[[d1_databases]]
binding = "DB"
database_name = "{DB_NAME}"
database_id = "{db_id}"
"""
    with open("wrangler.backend.toml", "w") as f:
        f.write(wrangler_content)

    # 5.1 Verify wrangler.backend.toml
    if os.path.exists("wrangler.backend.toml"):
        with open("wrangler.backend.toml", "r") as f:
            saved_content = f.read()
        if saved_content == wrangler_content:
            print("VERIFIED: 'wrangler.backend.toml' generated correctly.")
        else:
            print("FAILED: 'wrangler.backend.toml' content mismatch.")
    else:
        print("FAILED: 'wrangler.backend.toml' file not found after generation.")

    print("\n--- Setup Summary ---")
    print(f"Cloudflare Database: {DB_NAME} (ID: {db_id}) - VERIFIED")
    print(f"GitHub Secrets: {len(uploaded_secrets)} uploaded - VERIFIED")
    
    missing = [name for name, val in secrets_to_upload.items() if not val]
    if missing:
        print(f"MISSING SECRETS (Not in .env): {', '.join(missing)}")
        print("ADVICE: Add these to your .env with 'PROD_' prefix (e.g., PROD_SNEA_GITHUB_CLIENT_ID) and re-run.")
    
    if generated_jwt:
        print(f"\nIMPORTANT: A new JWT_SECRET was generated: {jwt_secret}")
        print("Please save this to your .env as PROD_JWT_SECRET to keep it consistent.")

    print("\nwrangler.backend.toml: Generated - VERIFIED")
    print("\nSetup Complete! 'wrangler.backend.toml' generated and secrets uploaded.")


if __name__ == "__main__":
    bootstrap()
