import os
import sys
from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

REPO_DIR = Path(__file__).resolve().parent.parent
REMOTE_URL = "https://github.com/aami672/YT-automate-agent.git"

print(f"Working in repository: {REPO_DIR}")

# 1. Initialize or open repository
if not (REPO_DIR / ".git").exists():
    repo = porcelain.init(str(REPO_DIR))
    print("Initialized new git repository.")
else:
    repo = Repo(str(REPO_DIR))
    print("Opened existing git repository.")

# 2. Stage all files (dulwich porcelain.add will scan workdir)
porcelain.add(str(REPO_DIR))
print("All files staged.")

# 3. Commit
try:
    commit_sha = porcelain.commit(
        str(REPO_DIR),
        message=b"feat: integrate universal Pixar 3D animated video engine with multi-character voices, BGM, and dissolve transitions",
        author=b"Amar <amar@example.com>",
        committer=b"Amar <amar@example.com>"
    )
    print(f"Committed changes with SHA: {commit_sha.decode('ascii') if isinstance(commit_sha, bytes) else commit_sha}")
except Exception as e:
    print(f"Commit note (may already be committed): {e}")

# 4. Configure remote origin
token = os.environ.get("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
if token:
    # Strip any https:// prefix if token was passed as full URL
    if "github.com" in token:
        target_remote = token
    else:
        target_remote = f"https://{token}@github.com/aami672/YT-automate-agent.git"
else:
    target_remote = REMOTE_URL

try:
    porcelain.remote_add(str(REPO_DIR), "origin", target_remote)
    print(f"Remote origin configured.")
except Exception as e:
    config = repo.get_config()
    config.set(("remote", "origin"), "url", target_remote.encode("utf-8"))
    config.write_to_path()
    print(f"Updated remote origin.")

# 5. Push to main branch
print("Pushing to remote repository (branch: main)...")
try:
    porcelain.push(str(REPO_DIR), "origin", "refs/heads/master:refs/heads/main", force=True)
    print("Push successful to refs/heads/main!")
except Exception as e1:
    try:
        porcelain.push(str(REPO_DIR), "origin", "refs/heads/main:refs/heads/main", force=True)
        print("Push successful to main!")
    except Exception as e2:
        print(f"Push result: {e2}")
        if "No valid credentials" in str(e2):
            print("\n[Authentication Required]: Please provide your GitHub Personal Access Token (PAT).")
            print("Usage: python scripts/push_to_git.py <YOUR_GITHUB_TOKEN>")

