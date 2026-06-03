# hermes-publish-html-skill

Tiny source repo for the `hermes-publish-html` Hermes skill.

## Install

```bash
hermes skills install https://raw.githubusercontent.com/RootMePLS/hermes-publish-html-skill/main/autonomous-ai-agents/hermes-publish-html/SKILL.md
```

Per profile:

```bash
hermes --profile family skills install https://raw.githubusercontent.com/RootMePLS/hermes-publish-html-skill/main/autonomous-ai-agents/hermes-publish-html/SKILL.md
hermes --profile vyndlo skills install https://raw.githubusercontent.com/RootMePLS/hermes-publish-html-skill/main/autonomous-ai-agents/hermes-publish-html/SKILL.md
```

## Required env

- `HERMES_PUBLISH_GATEWAY_URL`
- `HERMES_PUBLISH_GATEWAY_TOKEN`
- optional `HERMES_PUBLISH_TTL_DAYS`

## Layout

```text
autonomous-ai-agents/hermes-publish-html/
  SKILL.md
  scripts/publish_html_page.py
  references/distribute-to-profiles.md
```
