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
try:
    porcelain.remote_add(str(REPO_DIR), "origin", REMOTE_URL)
    print(f"Remote origin set to: {REMOTE_URL}")
except Exception as e:
    # Update remote URL if already exists
    config = repo.get_config()
    config.set(("remote", "origin"), "url", REMOTE_URL.encode("utf-8"))
    config.write_to_path()
    print(f"Updated remote origin to: {REMOTE_URL}")

# 5. Push to main branch
print(f"Pushing to {REMOTE_URL} (branch: main)...")
try:
    porcelain.push(str(REPO_DIR), "origin", "refs/heads/master:refs/heads/main", force=True)
    print("Push successful to refs/heads/main!")
except Exception as e1:
    print(f"Trying direct ref push: {e1}")
    try:
        porcelain.push(str(REPO_DIR), "origin", "refs/heads/main:refs/heads/main", force=True)
        print("Push successful to main!")
    except Exception as e2:
        print(f"Push result: {e2}")
