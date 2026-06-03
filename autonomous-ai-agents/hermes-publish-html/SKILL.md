---
name: hermes-publish-html
description: Use when Dmitrii explicitly asks to publish a substantial answer as an HTML page through the publish-gateway and return a link instead of dumping the full text into Telegram.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, telegram, publish, html, gateway, reports]
    related_skills: [hermes-agent]
---

# Hermes Publish HTML

## Overview

Use this when Dmitrii explicitly asks for HTML, a link, or a published page. The goal is simple: keep Telegram short, publish the real content through the publish-gateway, and return a link plus a compact preview.

This skill is **on-demand only**. Do not use it just because a reply is long. The trigger is the user's request, not your guesswork.

## When to Use

Use this skill when:
- the user says things like `publish`, `publish as html`, `make html`, `give me a link`, `send as a page`
- the output is substantial enough that a linked page is cleaner than a fat Telegram dump
- the user wants the artifact tied to the Hermes profile that handled the request

Do not use it when:
- the reply is short and chat-native is clearly better
- the user did not ask for HTML and a normal answer is fine
- the content contains secrets or material that should not be pushed into the publish-gateway

## Core Rules

1. **Explicit request only.** No automatic overflow behavior.
2. **Profile-scoped storage.** Keep a local source snapshot under the active profile's `workspace/publish-html/` tree.
3. **Short chat, long page.** In Telegram, send only a short preview and the link.
4. **Prefer markdown input.** Let the publish-gateway render the HTML page.
5. **No secret spraying.** If the content includes tokens, passwords, API keys, or sensitive raw dumps, stop and ask before publishing.

## Script

Primary helper script:
- `scripts/publish_html_page.py`

The script:
- reads markdown from a file or stdin
- publishes it to the configured publish-gateway
- stores a local source copy plus metadata under the active profile workspace
- prints JSON, a bare URL, or a short summary
- normalizes `source` into a dictionary payload for gateway compatibility, even when the caller passes a simple label string

## Required Environment

One of these must provide the values:
- environment variables in the current process
- the active profile `.env`
- the root `~/.hermes/.env`

Required:
- `HERMES_PUBLISH_GATEWAY_URL`
- `HERMES_PUBLISH_GATEWAY_TOKEN`

Optional:
- `HERMES_PUBLISH_TTL_DAYS`

## Recommended Workflow

1. Draft the full content in markdown.
2. Run the script with a title.
3. Read the returned URL.
4. Reply in Telegram with:
   - one sentence of context
   - the link
   - a very short preview or 2 to 4 bullets max

## Commands

From the active Hermes environment:

```bash
python "$HERMES_HOME/skills/autonomous-ai-agents/hermes-publish-html/scripts/publish_html_page.py" report.md --title "Report title"
```

Pipe content directly:

```bash
cat report.md | python "$HERMES_HOME/skills/autonomous-ai-agents/hermes-publish-html/scripts/publish_html_page.py" --title "Report title"
```

URL only:

```bash
cat report.md | python "$HERMES_HOME/skills/autonomous-ai-agents/hermes-publish-html/scripts/publish_html_page.py" --title "Report title" --output url
```

This is why the approach is profile-friendly: each Hermes profile has its own `HERMES_HOME`, skill install, `.env`, and `workspace/publish-html/` tree.

## Output Contract

Default output is JSON with:
- `url`
- `artifact_id`
- `expires_at`
- `profile`
- `stored_input_path`
- `stored_metadata_path`
- `title`
- `teaser`

Use that data to build the Telegram reply.

Reference notes:
- `references/publish-gateway-request-shape.md` — concise schema and compatibility note for the gateway request body, including the `source` object requirement.

## Telegram Reply Shape

Good pattern:
- first line: what the page is
- second line: link
- then a short preview only

Example shape:

```text
Published it here:
https://...

Short version:
- point one
- point two
- point three
```

## Pitfalls

1. **Trying to use this automatically.** That was the cursed branch talking. This skill is explicit-by-request.
2. **Publishing secrets.** The page is meant to be opened from a link. Treat it as externally retrievable.
3. **Forgetting the title.** Titles matter for page readability and local artifact naming.
4. **Confusing local snapshots with the served artifact.** The script stores the source locally; the publish-gateway hosts the rendered page.
5. **Assuming the current session will auto-load this new skill.** It will not. Use it in new sessions or load it explicitly.
6. **Sending `source` as a plain string to the gateway.** The current publish-gateway schema expects `source` to be an object/dictionary. If you hand-roll requests or refactor the script, keep that shape or you will eat a 422 for no good reason.

## Verification Checklist

- [ ] `HERMES_PUBLISH_GATEWAY_URL` resolves
- [ ] `HERMES_PUBLISH_GATEWAY_TOKEN` is present
- [ ] script returns a URL
- [ ] local source snapshot exists under `workspace/publish-html/`
- [ ] Telegram reply stays short and includes the link
