import os
import secrets
from cloudflare import Cloudflare
from github import Github
from nacl import public, encoding

# Configuration
ORG_NAME = "Brothertown-Language"
REPO_NAME = "snea-editor-private"
BACKEND_NAME = "snea-backend"
DB_NAME = "snea-shoebox"
DOMAIN = "michael-conrad.com"

def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return encoding.Base64Encoder.encode(encrypted).decode("utf-8")

def bootstrap():
    cf = Cloudflare(api_token=os.environ["CF_API_TOKEN"])
    gh = Github(os.environ["GH_TOKEN"])
    
    # 0. Get Repository from Organization
    print(f"Connecting to organization: {ORG_NAME}...")
    org = gh.get_organization(ORG_NAME)
    repo = org.get_repo(REPO_NAME)
    
    # 1. Create D1 Database
    print(f"Creating D1 database: {DB_NAME}...")
    account_id = cf.accounts.list()[0].id
    db = cf.d1.database.create(account_id=account_id, name=DB_NAME)
    print(f"Database Created! ID: {db.id}")
    
    # 2. Generate Secrets
    jwt_secret = secrets.token_urlsafe(32)
    
    # 3. Upload Secrets to GitHub
    public_key = repo.get_public_key()
    secrets_to_upload = {
        "CLOUDFLARE_API_TOKEN": os.environ["CF_API_TOKEN"],
        "CLOUDFLARE_ACCOUNT_ID": account_id,
        "JWT_SECRET": jwt_secret
    }
    
    for name, value in secrets_to_upload.items():
        print(f"Uploading secret {name}...")
        repo.create_secret(name, encrypt(public_key.key, value))
    
    # 4. Generate wrangler.toml
    with open("wrangler.toml", "w") as f:
        f.write(f'name = "{BACKEND_NAME}"\n')
        f.write('main = "src/worker.py"\n')
        f.write('compatibility_date = "2024-01-01"\n\n')
        f.write('[[d1_databases]]\n')
        f.write(f'binding = "DB"\n')
        f.write(f'database_name = "{DB_NAME}"\n')
        f.write(f'database_id = "{db.id}"\n')
    
    print("Setup Complete! 'wrangler.toml' generated and secrets uploaded.")

if __name__ == "__main__":
    bootstrap()
