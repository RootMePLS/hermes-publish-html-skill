# Publish gateway request shape

Concise note from a live smoke test.

## Durable compatibility fact

The current publish-gateway OpenAPI schema defines `PublishRequest.source` as an **object/dictionary**, not a string.

Relevant shape:

```json
{
  "profile": "default",
  "title": "Report title",
  "content": "# Markdown...",
  "content_format": "markdown",
  "ttl_days": 14,
  "source": {
    "label": "hermes-chat",
    "tool": "hermes-publish-html",
    "profile_home": "/Users/fishhead/.hermes",
    "profile": "default"
  }
}
```

## Symptom when wrong

If `source` is sent as a plain string like `"hermes-chat"`, the gateway returns HTTP 422 with a validation error similar to:

```text
Input should be a valid dictionary
loc: [body, source]
```

## What to do

- When using the packaged script, let it normalize `source`.
- When making raw requests, always send `source` as a dictionary.
- A minimal safe default is:

```json
{
  "label": "hermes-chat",
  "tool": "hermes-publish-html"
}
```

## Verification pattern

1. Publish a tiny markdown page.
2. Expect HTTP 200 and a JSON response with `url` and `artifact_id`.
3. Confirm the local snapshot and `metadata.json` exist under `workspace/publish-html/...`.
