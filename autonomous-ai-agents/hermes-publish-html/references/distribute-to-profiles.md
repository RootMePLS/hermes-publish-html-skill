# Distribute `hermes-publish-html` to other profiles

## Preferred long-term path

Use the git repo as the canonical source, then either:

1. install from the repo-style identifier through Hermes, or
2. run the helper script from a cloned checkout.

Canonical repo layout:

```text
<repo>/autonomous-ai-agents/hermes-publish-html/
  SKILL.md
  scripts/publish_html_page.py
  references/...
```

### Option A: Hermes install from the repo identifier

```bash
hermes --profile <profile-name> skills install RootMePLS/hermes-publish-html-skill/autonomous-ai-agents/hermes-publish-html --force
```

Why `--force` is needed: this is a community skill with a real Python script, so Hermes scans the whole directory and currently produces a `caution` verdict for routine `os.environ` / profile-handling code. Community + caution is blocked unless forced.

Why the raw `SKILL.md` URL is the wrong install target: Hermes treats direct URLs as **single-file skills only**. That path can install `SKILL.md`, but it will not fetch `scripts/` or `references/`, which makes this skill incomplete.

### Option B: install from a local git checkout

```bash
git clone https://github.com/RootMePLS/hermes-publish-html-skill.git
cd hermes-publish-html-skill
./install-from-git.sh --profile <profile-name>
```

This path is the least magical one. It copies the full skill directory exactly as-is, which is what you want when the scanner is being dramatic.

After install, make sure that target profile also has:
- `HERMES_PUBLISH_GATEWAY_URL`
- `HERMES_PUBLISH_GATEWAY_TOKEN`
- optional `HERMES_PUBLISH_TTL_DAYS`

Those belong in that profile's `.env` when the profile should publish independently.

## Immediate local-only path

If you just want it available in another local profile right now, copy the skill directory:

```bash
mkdir -p ~/.hermes/profiles/<profile-name>/skills/autonomous-ai-agents
cp -R ~/.hermes/skills/autonomous-ai-agents/hermes-publish-html \
  ~/.hermes/profiles/<profile-name>/skills/autonomous-ai-agents/
chmod +x ~/.hermes/profiles/<profile-name>/skills/autonomous-ai-agents/hermes-publish-html/scripts/publish_html_page.py
```

That is the blunt instrument version. It works. It is also the least elegant one, which is why git-backed install is the cleaner move.

## Sanity check inside a target profile

```bash
HERMES_HOME=~/.hermes/profiles/<profile-name> \
python ~/.hermes/profiles/<profile-name>/skills/autonomous-ai-agents/hermes-publish-html/scripts/publish_html_page.py --help
```

## Profile-scope behavior

The script writes local snapshots under:

```text
$HERMES_HOME/workspace/publish-html/YYYY/MM/DD/<artifact-id>/
```

So each profile keeps its own source copies and metadata automatically.
