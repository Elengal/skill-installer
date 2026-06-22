---
name: skill-installer
description: Install or refresh skill collections from a manifest file. Use this skill at the START of a session to ensure all needed skills are available, OR when you discover a skill is missing, OR when the user asks to "install skills" / "refresh skills" / "update skills". Also use proactively after a sandbox reset or when skill files are missing.
---

# Skill Installer

A meta-skill that installs/refreshes skill collections from a manifest file (`skills-manifest.json`). Each entry in the manifest clones an upstream repo and installs skills to the target directory.

## When to Use

**Use this skill:**
- At the START of a session, to ensure all skills are available
- When you try to use a skill and it's missing (e.g. `kc-review` not found)
- After a sandbox reset (skills are ephemeral — `/home/z/my-project/skills/` may be empty)
- When the user asks to "install skills", "refresh skills", "update skills"
- When you want to add a new skill collection (edit the manifest first)
- Proactively, before starting work that needs many skills

**Don't use this skill:**
- For trivial tasks where no skills are needed
- When only built-in Z.AI skills are needed (LLM, VLM, TTS, etc. — always available)

## The Manifest

The manifest lives at `/home/z/my-project/repos/skill-installer/skills-manifest.json`. It's a JSON file with:

```json
{
  "target_dir": "/home/z/my-project/skills",
  "repos": [
    {
      "name": "anthropic-official",
      "url": "https://github.com/anthropics/skills.git",
      "branch": "main",
      "prefix": "anthropic-",
      "source_path": "skills",
      "install_each_subdir": true,
      "description": "Anthropic official skills",
      "priority": 100
    }
  ]
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Identifier for the repo entry |
| `url` | ✅ | Git URL to clone |
| `branch` | Optional | Branch/tag (default: `main`) |
| `prefix` | Optional | Prepended to installed dir name |
| `source_path` | Optional | Subdirectory inside repo where skills live |
| `install_each_subdir` | Optional | If `true`, each subdir becomes its own collection |
| `target_name` | Optional | When `install_each_subdir=false`, name of installed dir |
| `skip` | Optional | Glob patterns to skip (e.g. `["*.zip"]`) |
| `filter` | Optional | `"has SKILL.md"` — only install subdirs with SKILL.md |
| `priority` | Optional | Higher = installed first (default: 50) |
| `description` | Optional | Human-readable description |

## How to Run

### Full install (all skills from manifest)

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py
```

### List what's in the manifest

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --list
```

### Install one repo only

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --repo anthropic-official
```

### Force reinstall (overwrite existing)

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --force
```

### Clean install (remove first, then install)

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --clean
```

### Dry run (show what would be done)

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --dry-run
```

### Custom manifest

```bash
python3 /home/z/my-project/repos/skill-installer/install_skills.py --manifest /path/to/custom.json
```

## Adding a New Skill Collection

1. Edit `skills-manifest.json` — add a new entry to the `repos` array
2. Run the installer: `python3 install_skills.py --repo <new-name>`
3. Verify the skill is installed: `ls /home/z/my-project/skills/ | grep <prefix>`
4. Update the `skill-dispatcher` catalog if the new skill should be discoverable

## Removing a Skill Collection

1. Edit `skills-manifest.json` — remove the entry
2. Manually delete the installed dirs: `rm -rf /home/z/my-project/skills/<prefix>*`
3. Or run `--clean` then reinstall (without the removed entry)

## How It Works

1. For each repo in the manifest (sorted by priority, highest first):
   - Clone with `--depth=1` to a temp directory
   - Navigate to `source_path` inside the cloned repo
   - If `install_each_subdir=true`: copy each subdirectory to `target_dir/<prefix><name>`
   - If `install_each_subdir=false`: copy the whole directory to `target_dir/<target_name>`
   - Skip patterns in `skip` (e.g. `.zip` files)
   - If `filter="has SKILL.md"`: only install subdirs that contain `SKILL.md`
   - Clean up temp dir
2. Up to 4 repos clone in parallel (configurable with `--parallel`)
3. Already-installed skills are skipped unless `--force`

## Key Design Decisions

- **Shallow clones** (`--depth=1`) — fast, no history
- **Parallel** by default — 4 repos at once
- **Idempotent** — running twice doesn't reinstall (unless `--force`)
- **Temp dirs** — no pollution of the repo
- **Manifest is source of truth** — edit JSON, not code
- **Priority-based** — important skills (Anthropic, OpenAI) install first
