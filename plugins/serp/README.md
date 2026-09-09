# SERP

**Author:** Ace Data Cloud

**Type:** Tool provider plugin

**API:** `https://api.acedata.cloud/serp/google`

**Source:** [AceDataCloud/Dify — SERP plugin](https://github.com/AceDataCloud/Dify/tree/main/plugins/serp)

## What it does

This plugin exposes the Ace Data Cloud Google SERP API as a Dify tool. It returns structured web, image, news, map, place, or video search results for use in workflows and agents.

## Tool

`serp_google` accepts:

- `query` (required);
- optional `type`, `country`, `language`, `range`, `number`, and `page`.

It returns `success`, `trace_id`, `data`, and `error` variables.

## Setup

1. [Create an Ace Data Cloud API token](https://platform.acedata.cloud/?utm_source=dify&utm_medium=plugin&utm_campaign=dify-serp).
2. In Dify, install the plugin and open its provider credentials.
3. Paste the token into `acedata_bearer_token` without the `Bearer` scheme.
4. Add **Google SERP** to a workflow or agent and run a test query.

The plugin calls only `https://api.acedata.cloud/serp/google`. See [PRIVACY.md](PRIVACY.md) for the exact query, credential, response, and retention boundaries.

## Packaging

From the repository root:

```bash
dify plugin package plugins/serp -o serp.difypkg
```
