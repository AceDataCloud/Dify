## Wan (Alibaba)

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/wan/videos`

### What it does

Integrates the **Ace Data Cloud Wan (Alibaba)** Videos API as a Dify tool for:

- Generating videos from a prompt (`text2video`)
- Generating videos from an image (`image2video`)

### Tools

- `wan_generate_video`
  - Inputs: `action` (required), `prompt`, `image_url`, `model`, `negative_prompt`, `resolution`, `duration`, `size`, `audio`, `audio_url`, `prompt_extend`, `shot_type`, `reference_video_urls`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data`, `error`

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/wan -o wan.difypkg
```
