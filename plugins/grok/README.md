## Grok

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/grok/videos`, `https://api.acedata.cloud/grok/tasks`

### What it does

This plugin integrates the **Ace Data Cloud Grok Imagine Videos API** as Dify tools for:

- Generating videos from a text prompt (text-to-video)
- Generating videos from an input image (image-to-video)
- Retrieving task status (`/grok/tasks`), single or batch

> Grok **chat** models (grok-4, grok-3, …) are available in Dify via the xAI / Ace Data Cloud model provider — this plugin covers Grok Imagine **video** generation.

### Tools

- `grok_generate_video`
  - Inputs: `prompt`, `image_url`, `model`, `reference_image_urls`, `aspect_ratio`, `resolution`, `duration`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data`, `error`
- `grok_task_retrieve`
  - Inputs: `task_id` (required)
  - Outputs: `success`, `data`, `error`
- `grok_task_retrieve_batch`
  - Inputs: `task_ids` (required)
  - Outputs: `success`, `data`, `error`

### Models

- `grok-imagine-video` (default) — text-to-video and image-to-video
- `grok-imagine-video-1.5-preview` — image-to-video only (requires `image_url`)

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/grok -o grok.difypkg
```
