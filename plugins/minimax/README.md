# MiniMax H3 Dify Plugin

AceDataCloud tool provider for MiniMax H3 multimodal video generation.

## Tools

- `minimax_generate_video`: generate 4–15 second video from text, 1–9 images, or 1–3 audio references
- `minimax_task_retrieve`: retrieve task status and final video

The generation tool supports 16:9 and 9:16, plus asynchronous submission and webhooks.

## Credential

Set `acedata_bearer_token` to an AceDataCloud API token without the `Bearer ` prefix.

## Package

```bash
dify plugin package plugins/minimax -o minimax.difypkg
```
