## Face Transform

**Author:** acedatacloud  
**Type:** tool provider plugin  
**API:** `https://api.acedata.cloud/face/{keypoints,beautify,age,gender,swap,cartoon,liveness}`

### What it does

Integrates the **Ace Data Cloud Face Transform API** as Dify tools for:

- Detecting 90+ face keypoints (`keypoints`)
- Beautifying portraits — smoothing, whitening, slimming, eye enlarging (`beautify`)
- Age / de-age transform (`age`)
- Gender swap (`gender`)
- Face swap between two images (`swap`)
- Cartoonize (`cartoon`)
- Liveness detection (`liveness`)

### Tools

- `face_transform`
  - Inputs: `action` (required), `image_url`, `source_image_url`, `target_image_url`, `smoothing`, `whitening`, `face_lifting`, `eye_enlarging`, `callback_url`
  - Outputs: `success`, `task_id`, `trace_id`, `data`, `error`

### Credentials

Requires `acedata_bearer_token` (paste the token without the `Bearer ` prefix).

### Packaging

```bash
dify plugin package plugins/face -o face.difypkg
```
