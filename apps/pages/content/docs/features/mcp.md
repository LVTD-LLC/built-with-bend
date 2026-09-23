---
title: MCP access
description: Connect a compatible agent using a curator profile credential.
---

# Connect an agent

The hosted MCP endpoint is `{{ mcp_url }}`. Access requires a profile credential issued privately by the operator. Public signup is closed.

Configure your MCP client for Streamable HTTP at `/mcp/`, with `Authorization: Bearer YOUR_PROFILE_KEY` or `X-API-Key: YOUR_PROFILE_KEY`. OAuth discovery and authorization are also available for existing operator-managed accounts.

The `get_user_info` tool checks which profile the credential represents. It does not publish projects. Use the separate [curator API](/docs/api-reference/introduction/) to add directory entries.

Never paste credentials into public submissions, repositories, or chat. The operator can rotate profile keys and disable accounts.
