# 🧠 Skill Installer

A lightweight, manifest-based skill installer for AI coding assistants. Instead of storing hundreds of megabytes of skill files in git, this repo stores only a **manifest** (`skills-manifest.json`) — a list of upstream repos to clone on demand.

## Why?

- **Lightweight**: 10 KB manifest vs 300 MB of skill files
- **Always fresh**: clones `--depth=1` from upstream `main` — latest version every time
- **Idempotent**: running twice won't reinstall (unless `--force`)
- **Parallel**: installs 4 repos at once by default
- **Selective**: install one repo, list what's available, dry-run
- **Sandbox-safe**: after a sandbox reset, one command restores everything

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

# Clean install (remove first, then install)
python3 install_skills.py --clean

# Dry run
python3 install_skills.py --dry-run
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
| `name` | ✅ | Identifier |
| `url` | ✅ | Git URL |
| `branch` | Optional | Branch/tag (default: `main`) |
| `prefix` | Optional | Prepended to installed dir name |
| `source_path` | Optional | Subdirectory inside repo |
| `install_each_subdir` | Optional | Each subdir → its own collection |
| `target_name` | Optional | Name when `install_each_subdir=false` |
| `skip` | Optional | Glob patterns to skip |
| `filter` | Optional | `"has SKILL.md"` to filter |
| `priority` | Optional | Higher = first (default: 50) |

## Current Collections (32 repos, ~1800 skills)

| Priority | Collection | Skills | Source |
|----------|------------|--------|--------|
| 100 | Anthropic official | 18 | [anthropics/skills](https://github.com/anthropics/skills) |
| 100 | OpenAI official | 39 | [openai/skills](https://github.com/openai/skills) |
| 95 | Vercel official | 9 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| 95 | Supabase official | 2 | [supabase/agent-skills](https://github.com/supabase/agent-skills) |
| 90 | Sentry official | 28 | [getsentry/sentry-skills](https://github.com/getsentry/sentry-skills) |
| 90 | UI UX Pro Max | 1 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| 85 | HashiCorp official | 3 | [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) |
| 85 | Agnix (linter) | 41 | [avifenesh/agnix](https://github.com/avifenesh/agnix) |
| 85 | VibeSec | 1 | [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) |
| 80 | Kepano (Obsidian) | 5 | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) |
| 75 | Superskills (ariadoss) | 39 | [ariadoss/superskills](https://github.com/ariadoss/superskills) |
| 75 | Awesome Toolkit | 40 | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) |
| 75 | Superartes | 17 | [andybrandt/superartes](https://github.com/andybrandt/superartes) |
| 75 | OilOil UI/UX Guide | 1 | [oil-oil/oiloil-ui-ux-guide](https://github.com/oil-oil/oiloil-ui-ux-guide) |
| 70 | Claude Code Superpowers | 16 | [TechyMT/claude-code-superpowers](https://github.com/TechyMT/claude-code-superpowers) |
| 70 | Kevinchamplin skills | 8 | [Kevinchamplin/claude-skills](https://github.com/Kevinchamplin/claude-skills) |
| 70 | ComposioHQ skills | 28 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) |
| 65 | Agent skills (PeterHdd) | 10 | [PeterHdd/agent-skills](https://github.com/PeterHdd/agent-skills) |
| 65 | Glebis skills | 94 | [glebis/claude-skills](https://github.com/glebis/claude-skills) |
| 60 | Artubss skills | 832 | [artubss/SKILLS-CLAUDE-CODE](https://github.com/artubss/SKILLS-CLAUDE-CODE) |
| 60 | Infrasity skills | 10 | [Infrasity-Labs/dev-gtm-claude-skills](https://github.com/Infrasity-Labs/dev-gtm-claude-skills) |
| 60 | Agryoutube | 2 | [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube) + [claude-blog](https://github.com/AgriciDaniel/claude-blog) |
| 50 | Favorites (premium) | 144 | artubss/SKILLS-CLAUDE-CODE |
| 50 | Plugins | 65 | artubss/SKILLS-CLAUDE-CODE |
| 50 | Coreyhanes marketing | 45 | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) |
| 50 | Rushik skills | 11 | [Rushik-Ghuntala/claude-code-skills](https://github.com/Rushik-Ghuntala/claude-code-skills) |
| 50 | LinkedIn skills | 1 | [Linked-API/linkedin-skills](https://github.com/Linked-API/linkedin-skills) |
| 50 | Telegram skills | 2 | [AlexSKuznetsov/claude-skill-telegram](https://github.com/AlexSKuznetsov/claude-skill-telegram) + [seedprod](https://github.com/seedprod/claude-code-telegram) |
| 50 | Sociilabs content writer | 1 | [sociilabs/claude-content-writer](https://github.com/sociilabs/claude-content-writer) |
| 50 | Glitternetwork PinMe | 1 | [glitternetwork/skills](https://github.com/glitternetwork/skills) |
| 40 | Raintree starter | 29 | [raintree-technology/claude-starter](https://github.com/raintree-technology/claude-starter) |

## Adding a New Collection

1. Edit `skills-manifest.json`
2. Add a new entry to the `repos` array
3. Run `python3 install_skills.py --repo <new-name>`
4. Verify: `ls /home/z/my-project/skills/ | grep <prefix>`

## License

MIT — the manifest and installer are free to use. Individual skills have their own licenses (check each upstream repo).
