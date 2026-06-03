# Distribute `hermes-publish-html` to other profiles

## Preferred long-term path

Put this skill directory in a tiny git repo or any static-hosted raw URL, then install it into each profile with Hermes.

Shape to publish:

```text
<repo>/autonomous-ai-agents/hermes-publish-html/
  SKILL.md
  scripts/publish_html_page.py
```

Then install into a target profile once the raw `SKILL.md` is reachable over HTTPS:

```bash
hermes --profile <profile-name> skills install https://raw.githubusercontent.com/RootMePLS/hermes-publish-html-skill/main/autonomous-ai-agents/hermes-publish-html/SKILL.md
```

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
