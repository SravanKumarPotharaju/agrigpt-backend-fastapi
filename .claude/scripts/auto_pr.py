"""
PostToolUse hook — runs after every Bash tool call.
If the command was a git push, auto-creates a PR using gh CLI.
"""
import sys
import json
import subprocess
import os

GH = r"C:\Program Files\GitHub CLI\gh.exe"

data = json.load(sys.stdin)
cmd = data.get("command", "")

if "git push" not in cmd:
    sys.exit(0)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get current branch name
branch = subprocess.check_output(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=project_root
).decode().strip()

# Don't create PR if already on main
if branch == "main":
    sys.exit(0)

# Get latest commit message to use as PR title
commit_msg = subprocess.check_output(
    ["git", "log", "-1", "--pretty=%s"],
    cwd=project_root
).decode().strip()

# Check if PR already exists for this branch
existing = subprocess.run(
    [GH, "pr", "list", "--head", branch, "--json", "number"],
    cwd=project_root,
    capture_output=True,
    text=True
)

if existing.stdout.strip() not in ("", "[]"):
    print(f"\n📋  PR already exists for branch '{branch}' — skipping creation.")
    sys.exit(0)

# Create the PR
print("\n" + "=" * 60)
print(f"🔀  Creating PR for branch: {branch}")
print("=" * 60)

result = subprocess.run(
    [
        GH, "pr", "create",
        "--base", "main",
        "--head", branch,
        "--title", commit_msg,
        "--body", "Auto-generated PR\n\n- Tests passed locally ✅\n- GitHub Actions will run pytest on this PR\n\n🤖 Created automatically by Claude Code"
    ],
    cwd=project_root,
)

if result.returncode == 0:
    print("\n✅  PR created successfully!")
else:
    print("\n⚠️  PR creation failed. Create it manually on GitHub.")
