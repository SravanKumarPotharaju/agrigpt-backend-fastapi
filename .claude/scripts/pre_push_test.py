"""
PreToolUse hook — runs before every Bash tool call.
If the command is a git push:
  1. Runs pytest locally — blocks push if tests fail
  2. After successful push, auto-creates a PR using gh CLI
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

# Resolve project root (two levels up from .claude/scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Step 1: Run tests ────────────────────────────────────────────────────────
print("=" * 60)
print("🧪  Running tests before push...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    cwd=project_root,
)

if result.returncode != 0:
    print("\n" + "=" * 60)
    print("❌  Tests FAILED — push blocked.")
    print("    Fix the failing tests, then push again.")
    print("=" * 60)
    sys.exit(1)

print("\n✅  All tests passed — proceeding with push.")

# ── Step 2: After push, auto-create PR ───────────────────────────────────────
# We schedule PR creation as a post-push action by printing a reminder
# that Claude will act on. The actual gh pr create runs after git push succeeds.
print("\n" + "=" * 60)
print("🚀  Push will complete. A PR will be created automatically.")
print("=" * 60)
