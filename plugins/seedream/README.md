# Seedream

**Author:** Ace Data Cloud

**Type:** Tool provider plugin

**API:** `https://api.acedata.cloud/seedream/images`

**Source:** [AceDataCloud/Dify — Seedream plugin](https://github.com/AceDataCloud/Dify/tree/main/plugins/seedream)

## What it does

This plugin adds image generation, reference-image editing, and editable-layer decomposition to Dify workflows and agents.

## Tools

- `seedream_generate_image` generates one image or a related image set from a prompt.
- `seedream_edit_image` edits one or more referenced images from a prompt.
- `seedream_decompose_image` splits one image into a base image and positioned layers.

Each tool returns `success`, `task_id`, `trace_id`, `data`, and `error` variables. Successful synchronous results also emit image messages for returned image URLs.

## Setup and reviewer check

1. [Create an Ace Data Cloud API token](https://platform.acedata.cloud/console/credentials?utm_source=dify&utm_medium=plugin&utm_campaign=dify-seedream).
2. Install the plugin in Dify and open its provider credentials.
3. Paste the token into `acedata_bearer_token` without the `Bearer` scheme.
4. Add **Seedream Generate Image** to a private test workflow, provide a short non-sensitive prompt, and run it synchronously.
5. Confirm `success=true`, a non-empty `data` array, an image message, and a `trace_id` that can be shared with support if troubleshooting is required.

Image generation and editing can consume credits. Review the [current Seedream pricing](https://platform.acedata.cloud/services/seedream?tab=pricing) before running the test. Do not put production secrets or sensitive source images in a reviewer workflow.

When `async=true`, the tool may return a task ID before media is ready. This plugin does not expose task retrieval, so use synchronous mode for the reviewer check and for workflows that require an inline image result.

## Data and support

The plugin calls only `https://api.acedata.cloud/seedream/images`. It sends the configured token in the `Authorization` header and sends only the tool inputs needed for the selected operation. See [PRIVACY.md](PRIVACY.md) for exact processing and retention boundaries.

- [Privacy policy](https://platform.acedata.cloud/privacy)
- [Terms](https://platform.acedata.cloud/terms)
- [Support](https://platform.acedata.cloud/support?utm_source=dify&utm_medium=plugin&utm_campaign=dify-seedream-support)
- [Report an issue](https://github.com/AceDataCloud/Dify/issues)
- Email: [office@acedata.cloud](mailto:office@acedata.cloud)

Last contract review: **2026-09-10**. The manifest intentionally remains `verified: false`; local validation does not represent Dify Marketplace approval or publication.

## Packaging

From the repository root:

```bash
dify plugin package plugins/seedream -o seedream.difypkg
```

The package excludes tests, local environment files, caches, and previously built packages through `.difyignore`.
