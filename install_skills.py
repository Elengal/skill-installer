#!/usr/bin/env python3
"""
Skill Installer — clones/updates skill collections from upstream repos.

Usage:
  python3 install_skills.py                    # install everything in manifest
  python3 install_skills.py --list             # show what would be installed
  python3 install_skills.py --repo anthropic   # install one repo by name
  python3 install_skills.py --force            # reinstall even if exists
  python3 install_skills.py --clean            # remove installed skills first
  python3 install_skills.py --parallel 4       # parallel clones (default 4)
  python3 install_skills.py --manifest custom.json  # use custom manifest

The manifest (skills-manifest.json) is the source of truth. Each entry defines:
- name: identifier
- url: git URL to clone
- branch: branch/tag/commit (default: main)
- prefix: prepended to installed dir name (e.g. "anthropic-" → "anthropic-frontend-design")
- source_path: subdirectory inside repo where skills live (e.g. "skills")
- install_each_subdir: if true, each subdir becomes its own skill collection
                       if false, the whole repo/source_path is one collection
- target_name: when install_each_subdir=false, the name of the installed dir
- skip: glob patterns to skip (e.g. ["*.zip"])
- filter: "has SKILL.md" — only install subdirs that contain SKILL.md
- priority: higher = installed first (default 50)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Colors for output
class C:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'

def c(text, color):
    return f"{color}{text}{C.RESET}"

def log(msg="", color=C.RESET, prefix=""):
    print(f"{prefix}{c(msg, color)}")

def run(cmd, cwd=None, timeout=120):
    """Run a shell command, return (success, output)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)

def git_clone_shallow(url, target, branch="main"):
    """Clone with --depth=1, return success."""
    cmd = ["git", "clone", "--depth", "1", "--branch", branch, url, target]
    ok, out = run(cmd, timeout=180)
    return ok, out

def install_repo(repo_entry, target_dir, force=False, dry_run=False):
    """
    Install one repo entry from the manifest.
    Returns (name, status, message, count_installed).
    """
    name = repo_entry["name"]
    url = repo_entry["url"]
    branch = repo_entry.get("branch", "main")
    prefix = repo_entry.get("prefix", "")
    source_path = repo_entry.get("source_path", "")
    install_each = repo_entry.get("install_each_subdir", False)
    target_name = repo_entry.get("target_name", "")
    skip_patterns = repo_entry.get("skip", [])
    filter_has_skill = repo_entry.get("filter") == "has SKILL.md"

    if dry_run:
        return name, "DRY", f"Would install from {url}", 0

    # Clone to temp dir
    with tempfile.TemporaryDirectory(prefix=f"skill-{name}-") as tmpdir:
        clone_target = Path(tmpdir) / "repo"
        ok, out = git_clone_shallow(url, str(clone_target), branch)
        if not ok:
            return name, "FAIL", f"Clone failed: {out[:200]}", 0

        # Find source dir
        if source_path:
            src_dir = clone_target / source_path
        else:
            src_dir = clone_target

        if not src_dir.exists():
            return name, "FAIL", f"Source path not found: {source_path}", 0

        installed = 0

        if install_each:
            # Each subdir becomes its own skill collection
            for sub in sorted(src_dir.iterdir()):
                if not sub.is_dir():
                    continue
                if sub.name.startswith("."):
                    continue
                # Skip patterns
                if any(_match_pattern(sub.name, p) for p in skip_patterns):
                    continue
                # Filter: must have SKILL.md
                if filter_has_skill and not (sub / "SKILL.md").exists():
                    continue

                dest = Path(target_dir) / f"{prefix}{sub.name}"
                if dest.exists():
                    if force:
                        shutil.rmtree(dest)
                    else:
                        # Skip
                        continue

                if dry_run:
                    installed += 1
                    continue

                try:
                    shutil.copytree(sub, dest)
                    installed += 1
                except Exception as e:
                    log(f"  {c('ERR', C.RED)} {prefix}{sub.name}: {e}", prefix="    ")
        else:
            # Whole source_path is one collection
            dest_name = target_name if target_name else f"{prefix}{name}"
            dest = Path(target_dir) / dest_name
            if dest.exists():
                if force:
                    shutil.rmtree(dest)
                else:
                    return name, "SKIP", f"Already installed: {dest_name}", 0

            if dry_run:
                return name, "DRY", f"Would install as {dest_name}", 1

            try:
                shutil.copytree(src_dir, dest)
                installed = 1
            except Exception as e:
                return name, "FAIL", f"Copy failed: {e}", 0

        return name, "OK", f"Installed {installed} skill(s)", installed

def _match_pattern(name, pattern):
    """Simple glob match."""
    import fnmatch
    return fnmatch.fnmatch(name, pattern)

def clean_dir(target_dir, manifest):
    """Remove directories that match manifest entries."""
    log(f"\n{c('Cleaning existing skills...', C.YELLOW)}")
    removed = 0
    for entry in manifest["repos"]:
        prefix = entry.get("prefix", "")
        source_path = entry.get("source_path", "")
        install_each = entry.get("install_each_subdir", False)
        target_name = entry.get("target_name", "")

        if install_each:
            # We don't know exact subdir names without cloning,
            # so we match by prefix
            if prefix:
                for d in Path(target_dir).glob(f"{prefix}*"):
                    if d.is_dir():
                        shutil.rmtree(d)
                        removed += 1
                        log(f"  {c('DEL', C.RED)} {d.name}", prefix="  ")
        else:
            dest_name = target_name if target_name else f"{prefix}{entry['name']}"
            d = Path(target_dir) / dest_name
            if d.exists():
                shutil.rmtree(d)
                removed += 1
                log(f"  {c('DEL', C.RED)} {dest_name}", prefix="  ")
    log(f"  Removed {removed} directories\n")

def main():
    parser = argparse.ArgumentParser(
        description="Install skill collections from manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--manifest", default="skills-manifest.json",
                        help="Path to manifest JSON (default: skills-manifest.json)")
    parser.add_argument("--target", default=None,
                        help="Target directory (default: from manifest)")
    parser.add_argument("--list", action="store_true",
                        help="List repos in manifest, don't install")
    parser.add_argument("--repo", default=None,
                        help="Install only this repo (by name)")
    parser.add_argument("--force", action="store_true",
                        help="Reinstall even if already installed")
    parser.add_argument("--clean", action="store_true",
                        help="Remove installed skills before installing")
    parser.add_argument("--parallel", type=int, default=4,
                        help="Number of parallel clones (default: 4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without doing it")
    args = parser.parse_args()

    # Load manifest
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        log(c(f"Manifest not found: {manifest_path}", C.RED))
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    target_dir = args.target or manifest.get("target_dir", "/home/z/my-project/skills")
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    repos = manifest["repos"]

    # Filter by --repo
    if args.repo:
        repos = [r for r in repos if r["name"] == args.repo]
        if not repos:
            log(c(f"Repo not found: {args.repo}", C.RED))
            log(f"Available: {', '.join(r['name'] for r in manifest['repos'])}")
            sys.exit(1)

    # Sort by priority (highest first)
    repos.sort(key=lambda r: r.get("priority", 50), reverse=True)

    # List mode
    if args.list:
        log(c(f"\n{'='*70}", C.CYAN))
        log(c(f"Skill Manifest — {len(repos)} repos", C.CYAN + C.BOLD))
        log(c(f"{'='*70}\n", C.CYAN))
        for r in repos:
            log(f"  {c(r['name'], C.BOLD)} (priority {r.get('priority', 50)})")
            log(f"    {c('URL:', C.BLUE)} {r['url']}")
            log(f"    {c('Prefix:', C.BLUE)} {r.get('prefix', '(none)')}")
            log(f"    {c('Source:', C.BLUE)} {r.get('source_path', '(root)')}")
            log(f"    {c('Mode:', C.BLUE)} {'each-subdir' if r.get('install_each_subdir') else 'whole-repo'}")
            if r.get('description'):
                log(f"    {c('Desc:', C.BLUE)} {r['description'][:100]}")
            log()
        log(c(f"Target dir: {target_dir}", C.CYAN))
        return

    # Clean mode
    if args.clean:
        clean_dir(target_dir, manifest)

    # Install
    log(c(f"\n{'='*70}", C.CYAN))
    log(c(f"Installing {len(repos)} skill collections → {target_dir}", C.CYAN + C.BOLD))
    log(c(f"{'='*70}\n", C.CYAN))

    start_time = time.time()
    results = []

    if args.parallel > 1:
        # Parallel installation
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {
                executor.submit(install_repo, r, target_dir, args.force, args.dry_run): r
                for r in repos
            }
            for future in as_completed(futures):
                r = futures[future]
                try:
                    name, status, msg, count = future.result()
                    results.append((name, status, msg, count))
                    _print_result(name, status, msg, count)
                except Exception as e:
                    results.append((r["name"], "ERR", str(e), 0))
                    _print_result(r["name"], "ERR", str(e), 0)
    else:
        # Sequential
        for r in repos:
            name, status, msg, count = install_repo(r, target_dir, args.force, args.dry_run)
            results.append((name, status, msg, count))
            _print_result(name, status, msg, count)

    # Summary
    elapsed = time.time() - start_time
    log(c(f"\n{'='*70}", C.CYAN))
    ok_count = sum(1 for _, s, _, _ in results if s == "OK")
    skip_count = sum(1 for _, s, _, _ in results if s == "SKIP")
    fail_count = sum(1 for _, s, _, _ in results if s in ("FAIL", "ERR"))
    total_skills = sum(c for _, _, _, c in results)
    log(c(f"Done in {elapsed:.1f}s — {ok_count} OK, {skip_count} skipped, {fail_count} failed", C.BOLD))
    log(c(f"Total skills installed: {total_skills}", C.BOLD))
    log(c(f"{'='*70}", C.CYAN))

    # Final count
    final_count = sum(1 for _ in Path(target_dir).rglob("SKILL.md"))
    log(f"\nTotal SKILL.md files in {target_dir}: {c(str(final_count), C.GREEN + C.BOLD)}")

    if fail_count > 0:
        sys.exit(1)

def _print_result(name, status, msg, count):
    color = {
        "OK": C.GREEN,
        "SKIP": C.YELLOW,
        "FAIL": C.RED,
        "ERR": C.RED,
        "DRY": C.CYAN,
    }.get(status, C.RESET)
    icon = {"OK": "✓", "SKIP": "→", "FAIL": "✗", "ERR": "!", "DRY": "?"}.get(status, "·")
    log(f"  {c(icon, color)} {c(name, C.BOLD)}: {msg} ({count} skills)", color=color)

if __name__ == "__main__":
    main()
