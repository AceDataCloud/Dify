## SeeDance

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/seedance/videos`

### What it does

This plugin integrates **Ace Data Cloud SeeDance Videos API** as Dify tools for:

- Generating videos from a prompt (optionally with reference images)

### Tools

- `seedance_generate_video`
  - Inputs: `prompt` (required), `model`, frame/reference image/audio/video URLs, `omni_reference_task_type`, `output_format`, `tools`, `return_last_frame`, `execution_expires_after`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data`, `error`

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/seedance -o seedance.difypkg
```


Seedance 2.5 (`doubao-seedance-2-5-260628`) supports up to 30 seconds, pure-audio and multimodal reference, and video edit/extend.
