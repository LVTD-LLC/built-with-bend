---
title: Curator API
description: Add projects with a private curator API key.
---

# Curator API

The directory ingestion endpoint is `POST /api/v1/projects`. Only active superusers may call it. Interactive [directory API documentation](/api/v1/docs) requires admin login.

Send `Authorization: Bearer YOUR_CURATOR_KEY` and a JSON body:

```json
{"title":"My Bend project","description":"What it does and how it uses Bend 2.","website_url":"https://example.com","sources":["https://github.com/example/project"],"publish":false}
```

At least one website, repository, or source URL is required. New projects default to private drafts. Set `publish` to true only after review. Duplicate primary URLs are rejected rather than overwritten.

The generated account API is separately available at `GET /api/user` with an operator-issued profile key. Profile/MCP keys are distinct from the directory ingestion key. No public signup is available.
