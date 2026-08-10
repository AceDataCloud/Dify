# MiniMax H3 Dify Plugin

AceDataCloud tool provider for MiniMax H3 multimodal video generation.

## Tools

- `minimax_generate_video`: generate 4–15 second video from text, 1–9 images, or 1–3 audio references
- `minimax_task_retrieve`: retrieve task status and final video

The generation tool accepts the MiniMax H3 V2 `content[]` format with the exact `MiniMax-H3` model identifier. It supports 768P and 2K, 16:9 and 9:16, asynchronous submission, and webhooks. Legacy flat fields such as `prompt`, `image_urls`, and `audio_urls` must be migrated into `content` items.

## Credential

Set `acedata_bearer_token` to an AceDataCloud API token without the `Bearer ` prefix.

## Package

```bash
dify plugin package plugins/minimax -o minimax.difypkg
```
