## Flux

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/flux/images`, `https://api.acedata.cloud/flux/tasks`

### What it does

This plugin integrates **Ace Data Cloud Flux Images Generation API** as Dify tools for:

- Generating images from a prompt
- Editing an image with a prompt and `image_url`
- Retrieving Flux task results

### Tools

- `flux_generate_image`
  - Inputs: `prompt` (required), `model`, `size`, `count`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data` (array), `error`
- `flux_edit_image`
  - Inputs: `prompt` (required), `image_url` (required), `model`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data` (array), `error`
- `flux_task_retrieve`
  - Inputs: `task_id` (required)
  - Outputs: `success`, `data`, `trace_id`, `error`
- `flux_task_retrieve_batch`
  - Inputs: `task_ids` (required)
  - Outputs: `success`, `data`, `trace_id`, `error`

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/flux -o flux.difypkg
```

