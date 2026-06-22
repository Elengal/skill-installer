---
name: skill-dispatcher
description: Meta-skill that helps choose the right skill for the current task. Use this skill whenever you are about to start non-trivial work and need to decide which skill(s) to apply, OR when you have multiple overlapping skills available and need to pick one. Also use proactively at the start of any task that involves planning, building, reviewing, testing, or designing — to avoid using the wrong skill or doing work from scratch when a skill exists for it. Especially useful when the user asks "which skill should I use" or when you find yourself hesitating between 2+ skills.
---

# Skill Dispatcher

A meta-skill for choosing the right skill for the job. The decision process is: **classify the task phase → look up candidate skills → pick by priority → announce choice before doing the work**.

## When to Use

Use this skill **before** starting any non-trivial task. Specifically:

- The user asks for something and you're unsure which skill applies
- You're hesitating between 2+ overlapping skills (e.g. `kc-review` vs `minimalist-review` vs `verify`)
- The task spans multiple phases (planning + building + testing)
- The user explicitly asks "which skill should I use?"
- You find yourself about to do work from scratch that *might* have a skill for it

**Do not use this skill** for:
- Trivial one-shot edits (typo fix, single value change)
- Conversational / informational questions
- Tasks where exactly one skill obviously applies

## The Core Problem This Solves

When you have 100+ skills available, two failure modes appear:

1. **Undertriggering** — doing work from scratch when a skill exists that would do it better
2. **Wrong-triggering** — picking a skill that's similar-but-not-right (e.g. `kc-review` when `artes-systematic-debugging` was needed)

This skill addresses both by making the selection process **explicit and auditable** before work begins.

## The Dispatch Process

### Step 1: Classify the task phase

Every non-trivial task fits into one or more of these phases:

| Phase | What happens | Trigger phrases |
|-------|--------------|-----------------|
| **Discover** | Understanding what user wants | "I want to...", "help me with...", "I need..." |
| **Plan** | Spec, requirements, design before code | "let's plan", "how should we...", "spec out" |
| **Build** | Writing implementation code | "implement", "build", "add feature", "make X" |
| **Review** | Checking existing work for issues | "review", "audit", "check", "find bugs" |
| **Debug** | Diagnosing unexpected behavior | "broken", "doesn't work", "error", "failing" |
| **Test** | Verifying behavior | "test", "verify", "qa", "make sure" |
| **Document** | Writing docs / content / files | "write doc", "create report", "make pdf" |
| **Deploy** | Shipping / finishing / releasing | "deploy", "release", "ship", "finish" |

A single user request often spans multiple phases. Identify all that apply.

### Step 2: Look up candidate skills

For each phase identified, consult the **Skill Catalog** in `references/skill-catalog.md`. That file contains the curated list of available skills grouped by phase, with selection criteria for each.

When multiple skills match the same phase, use these priority signals:

1. **Specificity** — a skill that exactly matches the task beats a general one
   - e.g. `toolkit-postgres-optimization` beats `db-optimize` for Postgres work
2. **Recency / authority** — `anthropic-*` skills are Anthropic-official, prefer them over community equivalents when in doubt
3. **Stack match** — if the skill mentions your exact stack (React, Next.js, Python), prefer it
4. **Scope match** — full-workflow skills (`artes-executing-plans`) beat point-tools (`tdd`) when the task is multi-step

### Step 3: Announce the choice

Before doing the work, state your skill selection explicitly. This makes the decision auditable and lets the user redirect if needed.

Use this format:

```
I'm using these skills for this task:
- Phase: <phase> → Skill: <skill-name> (why)
- Phase: <phase> → Skill: <skill-name> (why)

If you'd rather use a different skill, say so now.
```

If only one phase applies, simpler:

```
I'm using the <skill-name> skill for this task because <reason>.
```

### Step 4: Apply the skill(s) in phase order

If multiple phases are involved, apply them in the natural order:
Discover → Plan → Build → Review → Test → Document → Deploy

Each skill will announce itself when triggered — don't re-announce.

### Step 5: After the work, reflect briefly

One sentence: did the chosen skill(s) fit? If not, what would you pick next time? This builds a feedback loop for future dispatches.

## Worked Examples

### Example 1: "Add a new API endpoint to my Next.js app"

Phases: **Build** (implement endpoint) + **Test** (verify it works)

Candidates:
- Build: `fullstack-dev` (Next.js specific) — best match
- Test: `toolkit-testing-strategies` (general) or `playwright` (E2E) — depends on test type

Announce:
```
I'm using these skills for this task:
- Phase: Build → Skill: fullstack-dev (Next.js-specific fullstack work)
- Phase: Test → Skill: toolkit-testing-strategies (general testing patterns)

If you'd rather use a different skill, say so now.
```

### Example 2: "Review my code for bugs"

Phases: **Review**

Candidates:
- `kc-review` — quick security + quality scan of git diff
- `minimalist-review` — business-strategy review (not for code)
- `verify` — verification-before-completion (proves claims, doesn't find bugs)
- `artes-systematic-debugging` — for already-known bugs, not discovery
- `pentest` / `fuzz` / `toolkit-security-hardening` — security-specific

Pick: **`kc-review`** for general bug-finding on recent changes. If user mentioned security specifically → `toolkit-security-hardening`. If user mentioned "find the root cause of X" → `artes-systematic-debugging`.

### Example 3: "Make me a landing page for my SaaS"

Phases: **Plan** (design system) + **Build** (implement)

Candidates:
- Plan: `ui-ux-pro-max` (generates design system from project type) + `anthropic-frontend-design` (design principles)
- Build: `fullstack-dev` if Next.js, or `kc-frontend-design` for standalone HTML

Announce:
```
I'm using these skills for this task:
- Phase: Plan (design) → Skill: ui-ux-pro-max (generate design system) + anthropic-frontend-design (principles)
- Phase: Build → Skill: kc-frontend-design (distinctive, non-templated UI)

If you'd rather use a different skill, say so now.
```

### Example 4: "My server crashes with 0x80000003"

Phases: **Debug**

Candidates:
- `artes-systematic-debugging` — root cause investigation before fixing
- `debug` (superskills) — same approach, alternate name
- `kc-review` — only for code review, not runtime crashes
- `verify` — only for verifying claims, not diagnosing

Pick: **`artes-systematic-debugging`** — its "Iron Law: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST" is exactly right for a crash.

### Example 5: "Make a PDF report from this data"

Phases: **Document**

Candidates:
- `pdf` (Z.AI built-in) — generic PDF generation
- `anthropic-pdf` — Anthropic's production PDF skill
- `charts` — if data needs visualization first

Pick: **`anthropic-pdf`** (more authoritative) → if charts needed, **`charts`** first then **`anthropic-pdf`**.

### Example 6: "Make game art for my racing game"

Phases: **Plan** (art pipeline) + **Build** (generate assets)

Candidates:
- `ai-game-art-pipeline` — plan, generate prompts, post-process, package sprites
- `image-generation` (Z.AI) — AI image generation from prompts
- `spritesheet-*` — animated sprite sheets (GPT Image 2.0 pipeline)
- `design-blender-web-pipeline` — 3D models → web pipeline
- `gamestudio-*` — if full studio pipeline needed (designer + artist + QA)

Announce:
```
I'm using these skills for this task:
- Phase: Plan (art pipeline) → Skill: ai-game-art-pipeline (sprite pipeline planning)
- Phase: Build (generate) → Skill: image-generation (Z.AI AI image gen)
- Phase: Build (package) → Skill: ai-game-art-pipeline (clean, package, QA)
```

### Example 7: "Audit my game server for vulnerabilities"

Phases: **Review** (security audit)

Candidates:
- `hack-hack` — master entry, routes to specific attack domains
- `hack-api-sec` — API security (REST, GraphQL, auth, JWT)
- `hack-auth-sec` — authentication & authorization
- `hack-websocket-security` — WebSocket security
- `hack-injection-checking` — XSS, SQLi, SSRF, XXE routing
- `kc-review` — quick git diff scan
- `vibesec` — real-time security during coding
- `openai-security-threat-model` — architectural threat model

Pick: **Parallel subagent dispatch** — `kc-review` + `hack-api-sec` + `hack-auth-sec` + `hack-websocket-security` + `a11y` (5 subagents on same codebase, different lenses).

### Example 8: "Build a game in Unity/Godot"

Phases: **Plan** + **Build** + **Test**

Candidates:
- Unity: `unity-mcp` (if Editor running) or `vibe-gamedev` (JSON workflow)
- Godot: `godot-*` (Randroids) or `godot-am-*` (alexmeckes) or `godot-prompter-*`
- Full studio: `gamestudio-*` (49 agents, 72 skills)
- Art: `ai-game-art-pipeline` + `image-generation`
- Test: `toolkit-testing-strategies`

Pick: **`gamestudio-*`** for full pipeline, or **`godot-*`** / **`unity-mcp`** for specific engine.

## When NOT to Use a Skill

Sometimes the right answer is "no skill". Specifically:

- **Trivial fixes** — typo, single value, formatting. Just do it.
- **Free-form conversation** — chatting, brainstorming out loud, answering questions
- **Stack-specific niche** — if no skill matches your exact stack, do it from scratch but stay aware that a skill might exist
- **User explicitly says "don't use a skill"** — respect that

If you choose "no skill", state why briefly: "I'll do this from scratch because <reason>."

## Subagent Dispatch (Parallel Skill Execution)

**This is the key optimization.** When multiple skills apply to independent parts of a task, dispatch them to **subagents in parallel** instead of running them sequentially in your own context.

### Why subagents?

- **Isolated context:** Each subagent loads its own SKILL.md — your main context stays clean
- **Parallel execution:** 3 audits finish in ~time of 1
- **Focus:** Each subagent does ONE thing, no distraction
- **Token-efficient:** You only see the summaries, not all the intermediate work

### When to dispatch to subagents

```
Multiple skills could apply?
   ├─ No → Use skill directly in main context
   └─ Yes → Are they independent (no shared state)?
       ├─ No → Sequential in main context
       └─ Yes → Can run in parallel?
           ├─ No (e.g. need output of A as input to B) → Sequential subagents
           └─ Yes → PARALLEL DISPATCH ✓
```

Use parallel dispatch when:
- ✅ 2+ independent audits (security + accessibility + performance)
- ✅ 2+ independent feature implementations in different files
- ✅ 2+ independent test fixes (different test files, different bugs)
- ✅ Research + implementation can happen in parallel

**Don't** use parallel dispatch when:
- ❌ Tasks share state (same file, same DB)
- ❌ Need output of task A as input to task B
- ❌ Coordination overhead > parallelism gain (small tasks)
- ❌ User wants sequential, observable progress

### How to dispatch

Use the `Task` tool. For each subagent, craft a self-contained prompt:

```
Task tool call:
  subagent_type: "general-purpose"
  description: "Security audit"
  prompt: |
    You are doing a security audit of recent code changes.

    STEP 1: Read the skill file at:
    /home/z/my-project/skills/kc-review/SKILL.md

    STEP 2: Apply the skill to review these changes:
    [git diff or file paths]

    STEP 3: Return a structured report with:
    - Critical issues (must fix before deploy)
    - Warnings (should fix soon)
    - Notes (informational)

    Do NOT modify any files. Read-only audit.
```

**Critical rules for subagent prompts:**
1. **Skill path is explicit** — subagent doesn't know your skill inventory
2. **Task scope is explicit** — what to read, what to return
3. **Constraints are explicit** — read-only vs. can-modify
4. **No assumptions** — subagent doesn't see your conversation history

### Multiple subagents in one message

You CAN call `Task` multiple times in a single message — they run in parallel. Example:

```
// Single message, 3 parallel Task calls:

Task 1: subagent_type=general-purpose
  "Use kc-review skill on diff X. Return security issues."

Task 2: subagent_type=general-purpose
  "Use toolkit-security-hardening skill on diff X. Return OWASP issues."

Task 3: subagent_type=general-purpose
  "Use a11y skill on diff X. Return accessibility issues."
```

All three finish around the same time, you get 3 reports, you synthesize.

### Synthesis pattern

After parallel subagents return:

1. **Read all summaries** (they're short — that's the point)
2. **Deduplicate** — same issue found by 2 agents = mention once
3. **Categorize** — Critical / Warning / Note
4. **Present unified report** to user
5. **Credit the skills** — "Found via kc-review + toolkit-security-hardening + a11y"

### Subagent types available

| Type | Use for |
|------|---------|
| `general-purpose` | Most skill applications — flexible, has all tools |
| `Explore` | Quick research / file finding — fast, read-only |
| `Plan` | Architecture / implementation planning |
| `full-stack-developer` | Next.js fullstack implementation |
| `frontend-styling-expert` | CSS / styling work |
| `ppt-expert` | Slide deck creation |

Pick by what the skill needs. For most skill applications, `general-purpose` works.

### Common parallel patterns

**Parallel audit:**
```
Task 1: kc-review on diff → security issues
Task 2: toolkit-security-hardening on diff → OWASP issues
Task 3: a11y on diff → accessibility issues
```

**Parallel research:**
```
Task 1: web-search "best practices for X" → summary
Task 2: web-search "common pitfalls of X" → summary
Task 3: Explore codebase for existing patterns → summary
```

**Parallel implementation (independent files):**
```
Task 1: implement feature A in file1.js
Task 2: implement feature B in file2.js  (independent of A)
Task 3: write tests for both
```

**Parallel test fixes:**
```
Task 1: fix failing tests in fileA.test.js
Task 2: fix failing tests in fileB.test.js  (different root cause)
Task 3: fix failing tests in fileC.test.js  (different root cause)
```

### Anti-patterns

❌ **Don't** dispatch a subagent for a 30-second task — overhead > benefit
❌ **Don't** dispatch subagents that need to coordinate mid-task — they can't
❌ **Don't** forget to give subagent the skill path — it doesn't know
❌ **Don't** expect subagent to see your conversation — it can't
❌ **Don't** skip synthesis — multiple reports without synthesis = noise

## Conflict Resolution

When two skills could apply and you can't decide:

1. **Check the catalog notes** — `references/skill-catalog.md` includes selection hints
2. **Default to the more specific one** — `toolkit-postgres-optimization` > `db-optimize`
3. **Default to Anthropic-official** — `anthropic-frontend-design` > `kc-frontend-design`
4. **Default to the newer one** — when in doubt, the more recently updated skill wins (check `package.json` or skill version)
5. **Ask the user** — if still stuck, present 2-3 options with tradeoffs

## Skill Chains

Some tasks naturally chain skills. Common chains:

- **New feature**: `clarify` → `writing-plans` → `tdd` → `verify` → `kc-review`
- **Bug fix**: `artes-systematic-debugging` → fix → `verify` → `kc-review`
- **UI redesign**: `ui-ux-pro-max` (design system) → `anthropic-frontend-design` (principles) → `kc-frontend-design` (implement) → `anthropic-webapp-testing` (screenshot) → VLM critique
- **Deploy**: `qa-full` → `finish-branch`
- **Doc creation**: `content-writer` (draft) → `docx`/`pdf`/`pptx` (format)

When chaining, apply skills **sequentially in order**, not in parallel. Each skill's output feeds the next.

## Self-Improvement

This skill itself should evolve. When you find:

- A skill that's missing from the catalog → add it to `references/skill-catalog.md`
- A selection that didn't work well → add a note to the catalog explaining when NOT to pick it
- A new common chain → add it to "Skill Chains" above

The catalog is a living document. Edit it freely.

## Reference

- `references/skill-catalog.md` — full catalog of available skills by phase, with selection criteria
- `evals/evals.json` — test cases for this skill (see below)
