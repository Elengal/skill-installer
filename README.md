# 🧠 Skill Installer

A lightweight, manifest-based skill installer for AI coding assistants (Claude Code, Z.AI, and similar). Instead of storing hundreds of megabytes of skill files in git, this repo stores only a **manifest** (`skills-manifest.json`) — a list of upstream repos to clone on demand. One command restores the entire skill library after a sandbox reset.

## Why?

- **Lightweight**: ~25 KB manifest vs ~300 MB of skill files in git
- **Always fresh**: clones `--depth=1` from upstream default branch — latest version every run
- **Idempotent**: running twice won't reinstall (unless `--force`)
- **Parallel**: installs 8 repos at once by default (`--parallel N`)
- **Selective**: install one repo, list what's available, dry-run
- **Sandbox-safe**: after a sandbox reset, one command restores everything
- **Meta-skills included**: ships with `skill-dispatcher` (smart skill routing) as a local skill

## What's in the Box

- **1 local meta-skill**: `skill-dispatcher` — classifies the task → picks the right skill → applies → reflects
- **52 upstream repos** organized by priority (100 → 40)
- **~2150 individual skills** after a full install (as of the last manifest update)
- Covers: official vendor skills (Anthropic, OpenAI, Vercel, Supabase, Sentry, HashiCorp), UI/UX, security/pentest, Obsidian, game development (Godot, Unity, Three.js), marketing, content writing, Telegram/LinkedIn integrations, and more

## Quick Start

```bash
# Install ALL skills from the manifest
python3 install_skills.py

# List what's in the manifest
python3 install_skills.py --list

# Install one repo only
python3 install_skills.py --repo anthropic-official

# Force reinstall (overwrite existing)
python3 install_skills.py --force

# Reinstall one specific repo with --force
python3 install_skills.py --repo godot-claude-skills --force

# Clean install (remove first, then install)
python3 install_skills.py --clean

# Dry run (show what would be done)
python3 install_skills.py --dry-run

# Custom parallelism (default 4)
python3 install_skills.py --parallel 8

# Custom manifest
python3 install_skills.py --manifest /path/to/custom.json
```

## The Manifest

`skills-manifest.json` is the source of truth. Each entry defines how to clone and install a skill collection:

```json
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
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Identifier for the repo entry |
| `url` | ✅ | Git URL to clone |
| `branch` | Optional | Branch/tag (default: `main`). Use the upstream default branch. |
| `prefix` | Optional | Prepended to installed dir name (e.g. `anthropic-` → `anthropic-frontend-design`) |
| `source_path` | Optional | Subdirectory inside repo where skills live (e.g. `skills`, `.claude/skills`, `.agents/skills`) |
| `install_each_subdir` | Optional | If `true`, each subdir becomes its own skill collection. If `false`/absent, the whole `source_path` is one collection. |
| `target_name` | Optional | When `install_each_subdir=false`, name of installed dir |
| `skip` | Optional | Glob patterns to skip (e.g. `["*.zip"]`) |
| `filter` | Optional | `"has SKILL.md"` — only install subdirs containing `SKILL.md` |
| `priority` | Optional | Higher = installed first (default: 50) |
| `description` | Optional | Human-readable description (shown in `--list`) |

### Notes on `source_path`

Skill collections live in different places depending on the upstream repo's convention. Common patterns observed:

- `skills/` — most common (Anthropic, OpenAI, Vercel, Supabase, Sentry, …)
- `.claude/skills/` — Claude Code convention (claude-code-game-studios)
- `.agents/skills/` — agent-first repos (vibejam-starter-pack)
- root `""` — when SKILL.md files are scattered or at top level

If a repo installs **0 skills**, the first thing to check is whether `source_path` matches where the upstream `SKILL.md` files actually live. Clone the repo manually and run `find . -name SKILL.md` to find the correct path.

## How It Works

1. For each repo in the manifest (sorted by priority, highest first):
   - Clone with `git clone --depth=1 --branch <branch>` to a temp directory
   - Navigate to `source_path` inside the cloned repo
   - If `install_each_subdir=true`: copy each subdirectory to `target_dir/<prefix><name>`
   - If `install_each_subdir=false`: copy the whole directory to `target_dir/<target_name>`
   - Skip patterns in `skip` (e.g. `.zip` files)
   - If `filter="has SKILL.md"`: only install subdirs that contain `SKILL.md`
   - Clean up temp dir
2. Up to N repos clone in parallel (`--parallel N`, default 4)
3. Already-installed skills are skipped unless `--force`

## Default Target

The default install directory is `/home/z/my-project/skills/` (set in the manifest's `target_dir` field). Override with `--target /your/path`.

## Current Collections (52 repos, ~2150 skills)

Skill counts below are from a real full install with the current manifest. Counts may drift as upstream repos add new skills.

### Priority 100 — Official vendor skills

| Collection | Installed | Source |
|------------|-----------|--------|
| anthropic-official | 17 | [anthropics/skills](https://github.com/anthropics/skills) |
| openai-official | 39 | [openai/skills](https://github.com/openai/skills) |

### Priority 95 — Official vendor skills (cont.)

| Collection | Installed | Source |
|------------|-----------|--------|
| vercel-official | 9 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| supabase-official | 2 | [supabase/agent-skills](https://github.com/supabase/agent-skills) |

### Priority 85–90 — High-value collections

| Collection | Installed | Source |
|------------|-----------|--------|
| sentry-official | 28 | [getsentry/sentry-skills](https://github.com/getsentry/sentry-skills) |
| ui-ux-pro-max | 1 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| pro-workflow-skills | 41 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| pro-workflow-agents | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| pro-workflow-rules | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| pro-workflow-references | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| pro-workflow-commands | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| pro-workflow-scripts | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| hashicorp-official | 3 | [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) |
| agnix (linter) | 1 | [avifenesh/agnix](https://github.com/avifenesh/agnix) |
| vibesec | 1 | [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) |

### Priority 75–80 — Curated large collections

| Collection | Installed | Source |
|------------|-----------|--------|
| kepano-obsidian | 5 | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) |
| pro-workflow-references | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| hack-skills (security) | 102 | [yaklang/hack-skills](https://github.com/yaklang/hack-skills) |
| ai-game-art-pipeline | 1 | [ybuild-ai/ai-game-art-pipeline-skill](https://github.com/ybuild-ai/ai-game-art-pipeline-skill) |
| superskills-ariadoss | 39 | [ariadoss/superskills](https://github.com/ariadoss/superskills) |
| awesome-claude-code-toolkit | 40 | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) |
| superartes | 17 | [andybrandt/superartes](https://github.com/andybrandt/superartes) |
| oiloil-ui-ux-guide | 1 | [oil-oil/oiloil-ui-ux-guide](https://github.com/oil-oil/oiloil-ui-ux-guide) |
| claude-code-game-studios | 73 | [donchitos/claude-code-game-studios](https://github.com/donchitos/claude-code-game-studios) |

### Priority 65–70 — Community skills

| Collection | Installed | Source |
|------------|-----------|--------|
| claude-code-superpowers | 16 | [TechyMT/claude-code-superpowers](https://github.com/TechyMT/claude-code-superpowers) |
| claude-skills-kevinchamplin | 8 | [Kevinchamplin/claude-skills](https://github.com/Kevinchamplin/claude-skills) |
| composio-skills | 28 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) |
| agent-skills-peterhdd | 10 | [PeterHdd/agent-skills](https://github.com/PeterHdd/agent-skills) |
| glebis-skills | 81 | [glebis/claude-skills](https://github.com/glebis/claude-skills) |
| godot-claude-skills | 57 | [Randroids-Dojo/Godot-Claude-Skills](https://github.com/Randroids-Dojo/Godot-Claude-Skills) |
| godot-claude-skills-alexmeckes | 5 | [alexmeckes/godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills) |
| godot-prompter | 51 | [jame581/GodotPrompter](https://github.com/jame581/GodotPrompter) |
| pro-workflow-hooks-config | 1 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) |
| unity-mcp | 0 (whole-repo) | [IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP) |
| ai-game-spritesheets | 0 | [chongdashu/ai-game-spritesheets](https://github.com/chongdashu/ai-game-spritesheets) |
| claude-design-skills | 23 | [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills) |

### Priority 50–60 — Niche & marketing

| Collection | Installed | Source |
|------------|-----------|--------|
| artubss-skills | 26 | [artubss/SKILLS-CLAUDE-CODE](https://github.com/artubss/SKILLS-CLAUDE-CODE) |
| artubss-favorites | 1 | [artubss/SKILLS-CLAUDE-CODE](https://github.com/artubss/SKILLS-CLAUDE-CODE) |
| artubss-plugins | 1 | [artubss/SKILLS-CLAUDE-CODE](https://github.com/artubss/SKILLS-CLAUDE-CODE) |
| infrasity-skills | 11 | [Infrasity-Labs/dev-gtm-claude-skills](https://github.com/Infrasity-Labs/dev-gtm-claude-skills) |
| agryoutube-youtube | 1 | [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube) |
| agryoutube-blog | 1 | [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog) |
| vibe-gamedev | 1 | [ryholmdahl/vibe-gamedev](https://github.com/ryholmdahl/vibe-gamedev) |
| vibejam-starter-pack | 8 | [chongdashu/vibejam-starter-pack](https://github.com/chongdashu/vibejam-starter-pack) |
| godogen | 0 | [htdt/godogen](https://github.com/htdt/godogen) |
| coreyhaines-marketing | 2 | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) |
| rushik-skills | 5 | [Rushik-Ghuntala/claude-code-skills](https://github.com/Rushik-Ghuntala/claude-code-skills) |
| linkedin-skills | 1 | [Linked-API/linkedin-skills](https://github.com/Linked-API/linkedin-skills) |
| alexskuznetsov-telegram | 1 | [AlexSKuznetsov/claude-skill-telegram](https://github.com/AlexSKuznetsov/claude-skill-telegram) |
| seedprod-daily-brief | 1 | [seedprod/claude-code-telegram](https://github.com/seedprod/claude-code-telegram) |
| sociilabs-content-writer | 1 | [sociilabs/claude-content-writer](https://github.com/sociilabs/claude-content-writer) |
| glitternetwork-pinme | 1 | [glitternetwork/skills](https://github.com/glitternetwork/skills) |

### Priority 40 — Starter packs

| Collection | Installed | Source |
|------------|-----------|--------|
| raintree-claude-starter | 1 | [raintree-technology/claude-starter](https://github.com/raintree-technology/claude-starter) |

### Repos with 0 installs

A few repos currently install 0 skills. These are kept in the manifest for visibility — they may be fixed in a future update, or the upstream may not yet publish `SKILL.md` files at the expected location:

- `unity-mcp` — installed as a whole-repo collection (not via subdirs), so the count shows 0 but the directory exists
- `ai-game-spritesheets` — no `SKILL.md` files in the repo
- `godogen` — complex multi-engine layout (`godot/skills/`, `bevy/skills/`, `babylon/skills/`); not yet mapped

## Adding a New Collection

1. Edit `skills-manifest.json` — add a new entry to the `repos` array
2. Run the installer for just that repo: `python3 install_skills.py --repo <new-name>`
3. Verify the skill is installed: `ls /home/z/my-project/skills/ | grep <prefix>`
4. If 0 skills install, clone the repo manually and run `find . -name SKILL.md` to find the correct `source_path`

### Example entry

```json
{
  "name": "my-new-collection",
  "url": "https://github.com/user/repo.git",
  "branch": "main",
  "prefix": "mycol-",
  "source_path": "skills",
  "install_each_subdir": true,
  "filter": "has SKILL.md",
  "description": "What this collection does",
  "priority": 60
}
```

## Removing a Skill Collection

1. Edit `skills-manifest.json` — remove the entry
2. Manually delete the installed dirs: `rm -rf /home/z/my-project/skills/<prefix>*`
3. Or run `--clean` then reinstall (without the removed entry)

## Verifying an Install

After running the installer, you can sanity-check the result:

```bash
# Total SKILL.md files installed
find /home/z/my-project/skills -name SKILL.md | wc -l

# Skills from a specific collection
ls /home/z/my-project/skills/ | grep '^anthropic-'

# All installed top-level skill directories
ls /home/z/my-project/skills/ | wc -l
```

## Files in This Repo

| File | Purpose |
|------|---------|
| `install_skills.py` | The installer — clone, copy, parallel, dry-run, force, clean |
| `skills-manifest.json` | The manifest — the single source of truth for what gets installed |
| `skill-installer/SKILL.md` | Self-describing skill file (so this repo can be invoked as a skill by Claude Code) |
| `skills/skill-dispatcher/` | Local meta-skill — routes tasks to the right installed skill |
| `README.md` | This file |

## Design Decisions

- **Shallow clones** (`--depth=1`) — fast, no history
- **Parallel by default** — 4 repos at once (tunable with `--parallel`)
- **Idempotent** — running twice doesn't reinstall (unless `--force`)
- **Temp dirs** — no pollution of the repo
- **Manifest is source of truth** — edit JSON, not code
- **Priority-based** — important skills (Anthropic, OpenAI) install first
- **No tokens required** — all upstream repos are public; the installer just clones them

## License

MIT — the manifest and installer are free to use. Individual skills have their own licenses (check each upstream repo).

## Acknowledgements

Thanks to all the upstream skill authors whose collections make this manifest useful. The full list of source repos is in `skills-manifest.json` and in the collection tables above.
