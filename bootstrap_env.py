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
PAGES_NAME = os.getenv("PAGES_NAME", "snea-shoebox-editor")
DB_NAME = os.getenv("DB_NAME", "snea-shoebox")
DOMAIN = os.getenv("DOMAIN", "michael-conrad.com")
BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN", f"snea-backend.{DOMAIN}")
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", f"snea-editor.{DOMAIN}")


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return encoding.Base64Encoder.encode(encrypted).decode("utf-8")


def bootstrap():
    # Cloudflare Initialization: Prefer Global API Key/Email for D1 operations as per SDK requirements
    cf_email = os.getenv("PROD_CF_EMAIL")
    cf_key = os.getenv("PROD_CF_API_KEY")
    cf_token = os.getenv("PROD_CF_API_TOKEN")

    if cf_email and cf_key:
        print("Initializing Cloudflare client with Global API Key...")
        cf = Cloudflare(api_email=cf_email, api_key=cf_key)
    elif cf_token:
        print("Initializing Cloudflare client with User API Token (Warning: D1 operations may fail)...")
        cf = Cloudflare(api_token=cf_token)
    else:
        raise Exception("Missing Cloudflare credentials. Provide PROD_CF_EMAIL and PROD_CF_API_KEY (Recommended) or PROD_CF_API_TOKEN in .env")

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

    # 2. Configure Custom Domains (Cloudflare)
    # Note: If this fails or domains don't appear, use bootstrap_domains.py
    print(f"Configuring Custom Domains on Cloudflare...")
    try:
        # Check if the domain zone exists
        print(f"Verifying zone for domain '{DOMAIN}'...")
        zones = list(cf.zones.list(name=DOMAIN))
        if not zones:
            print(f"WARNING: Zone for '{DOMAIN}' not found in this Cloudflare account.")
            print(f"Custom domains can only be configured for zones managed by this account.")
        else:
            print(f"SUCCESS: Zone '{DOMAIN}' found (ID: {zones[0].id}).")

        # Worker Custom Domain
        print(f"Ensuring Custom Domain '{BACKEND_DOMAIN}' for Worker '{BACKEND_NAME}'...")
        # The Cloudflare Python SDK uses different signatures depending on the version.
        try:
            # Attempt 1: Standard documented update
            cf.workers.domains.update(
                account_id=account_id,
                domain_name=BACKEND_DOMAIN,
                service=BACKEND_NAME,
                environment="production",
            )
            print(f"SUCCESS: Worker domain '{BACKEND_DOMAIN}' configured.")
        except (TypeError, Exception) as e1:
            try:
                # Attempt 2: Positional domain_name
                cf.workers.domains.update(
                    BACKEND_DOMAIN,
                    account_id=account_id,
                    service=BACKEND_NAME,
                    environment="production",
                )
                print(f"SUCCESS: Worker domain '{BACKEND_DOMAIN}' configured.")
            except (TypeError, Exception) as e2:
                try:
                    # Attempt 3: hostname keyword
                    cf.workers.domains.update(
                        account_id=account_id,
                        hostname=BACKEND_DOMAIN,
                        service=BACKEND_NAME,
                        environment="production",
                    )
                    print(f"SUCCESS: Worker domain '{BACKEND_DOMAIN}' configured.")
                except (TypeError, Exception) as e3:
                    print(f"Failed to configure Worker domain via SDK: {e3}")
                    print(f"Manual step might be required for Worker domain '{BACKEND_DOMAIN}'.")

        # Pages Custom Domain
        print(f"Ensuring Custom Domain '{FRONTEND_DOMAIN}' for Pages project '{PAGES_NAME}'...")
        try:
            cf.pages.projects.domains.create(
                account_id=account_id,
                project_name=PAGES_NAME,
                name=FRONTEND_DOMAIN,
            )
            print(f"SUCCESS: Pages domain '{FRONTEND_DOMAIN}' configured.")
        except Exception as ep:
            if "already exists" in str(ep).lower():
                print(f"SUCCESS: Pages domain '{FRONTEND_DOMAIN}' already exists.")
            else:
                print(f"Failed to configure Pages domain: {ep}")
                print(f"Manual step might be required for Pages domain '{FRONTEND_DOMAIN}'.")
                
    except Exception as e:
        print(f"Warning/Error during domain configuration: {e}")
        print("Note: If domains are already configured or the project/worker hasn't been deployed yet, this might show an error.")

    # 3. Generate Secrets
    jwt_secret = secrets.token_urlsafe(32)

    # 4. Upload Secrets to GitHub
    public_key = repo.get_public_key()
    
    github_client_id = os.environ.get("PROD_GITHUB_CLIENT_ID")
    github_client_secret = os.environ.get("PROD_GITHUB_CLIENT_SECRET")
    
    secrets_to_upload = {
        "CLOUDFLARE_API_TOKEN": cf_token or os.environ.get("PROD_CF_API_TOKEN"),
        "CLOUDFLARE_ACCOUNT_ID": account_id,
        "JWT_SECRET": jwt_secret,
        "SNEA_GITHUB_CLIENT_ID": github_client_id,
        "SNEA_GITHUB_CLIENT_SECRET": github_client_secret,
    }

    for name, value in secrets_to_upload.items():
        if value:
            print(f"Uploading secret {name}...")
            repo.create_secret(name, encrypt(public_key.key, value))
        else:
            print(f"Skipping secret {name} (not found in .env)")

    # 5. Generate wrangler.toml
    with open("wrangler.toml", "w") as f:
        f.write(f'name = "{BACKEND_NAME}"\n')
        f.write('main = "src/worker.py"\n')
        f.write('compatibility_date = "2024-01-01"\n\n')
        f.write("[[d1_databases]]\n")
        f.write('binding = "DB"\n')
        f.write(f'database_name = "{DB_NAME}"\n')
        f.write(f'database_id = "{db_id}"\n')

    print("Setup Complete! 'wrangler.toml' generated and secrets uploaded.")


if __name__ == "__main__":
    bootstrap()
