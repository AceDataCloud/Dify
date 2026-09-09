# Seedance

**Author:** Ace Data Cloud

**Type:** Tool provider plugin

**API:** `https://api.acedata.cloud/seedance/videos`

**Source:** [AceDataCloud/Dify — Seedance plugin](https://github.com/AceDataCloud/Dify/tree/main/plugins/seedance)

## What it does

This plugin adds text-to-video and reference-driven video generation to Dify workflows and agents. Seedance 2.5 supports multimodal image, audio, and video references, video edit or extension tasks, optional audio, and videos up to 30 seconds when the selected parameters are compatible.

## Tool

`seedance_generate_video` accepts a prompt, model, frame or reference media URLs, output settings, and optional execution controls. It returns `success`, `task_id`, `trace_id`, `data`, and `error` variables.

## Setup and reviewer check

1. [Create an Ace Data Cloud API token](https://platform.acedata.cloud/console/credentials?utm_source=dify&utm_medium=plugin&utm_campaign=dify-seedance).
2. Install the plugin in Dify and open its provider credentials.
3. Paste the token into `acedata_bearer_token` without the `Bearer` scheme.
4. Add **Seedance Generate Video** to a private test workflow, provide a short non-sensitive prompt, leave `async` disabled, and run it.
5. Confirm `success=true`, `data` contains the completed video result, and a `trace_id` is available for support.

Video generation can consume credits. Review the [current Seedance pricing](https://platform.acedata.cloud/services/seedance?tab=pricing) before running the test. Referenced media must be content you are authorized to process.

When `async=true` or a callback URL is supplied, the API may return a task ID before media is ready. This plugin does not expose task retrieval, so use synchronous mode for the reviewer check and for workflows that require an inline video result. Use a callback only when you control a real reachable webhook; do not use a health endpoint as a placeholder callback.

## Data and support

The plugin calls only `https://api.acedata.cloud/seedance/videos`. It sends the configured token in the `Authorization` header and sends only the tool inputs needed for generation. See [PRIVACY.md](PRIVACY.md) for exact processing and retention boundaries.

- [Privacy policy](https://platform.acedata.cloud/privacy)
- [Terms](https://platform.acedata.cloud/terms)
- [Support](https://platform.acedata.cloud/support?utm_source=dify&utm_medium=plugin&utm_campaign=dify-seedance-support)
- [Report an issue](https://github.com/AceDataCloud/Dify/issues)
- Email: [office@acedata.cloud](mailto:office@acedata.cloud)

Last contract review: **2026-09-10**. The manifest intentionally remains `verified: false`; local validation does not represent Dify Marketplace approval or publication.

## Packaging

From the repository root:

```bash
dify plugin package plugins/seedance -o seedance.difypkg
```

The package excludes tests, local environment files, caches, and previously built packages through `.difyignore`.
