## Fish Audio

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/fish/audios`

### What it does

Integrates the **Ace Data Cloud Fish Audio API** as a Dify tool for synthesizing text-to-speech audio.

### Tools

- `fish_generate_audio`
  - Inputs: `text` (required), `reference_id`, `model`, `format`, `sample_rate`, `mp3_bitrate`, `latency`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data`, `error`

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/fish -o fish.difypkg
```
