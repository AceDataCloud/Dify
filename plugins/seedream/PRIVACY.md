# Privacy

This policy describes the data flow of the Ace Data Cloud Seedream plugin for Dify.

## Data processed

When a tool runs, the plugin processes:

- the Ace Data Cloud bearer token configured in Dify;
- the prompt and selected generation options;
- image URLs or image strings supplied for editing or layer decomposition;
- callback URL when the user explicitly provides one;
- generated image metadata, task ID, error details, and trace ID returned by the API.

Prompts and images may contain personal or confidential information. Do not submit content that you are not authorized to process.

## Data transfer

The plugin sends the selected inputs over HTTPS only to the fixed endpoint `https://api.acedata.cloud/seedream/images`. The bearer token is sent only in the `Authorization` header. The plugin does not expose a configurable destination host.

The response is returned to the Dify workflow. The plugin does not send data to advertising or analytics services and contains no telemetry code. A callback URL is sent only when the user explicitly configures it; that destination then receives data according to the user's workflow design.

## Storage and retention

The plugin does not write prompts, images, responses, or credentials to local files or its own database. Dify controls how plugin credentials, workflow inputs, outputs, and execution logs are stored and retained. Data processed by Ace Data Cloud is subject to the [Ace Data Cloud Privacy Policy](https://platform.acedata.cloud/privacy).

Generated URLs may expire. Users who need durable artifacts must save them in storage they control and are authorized to use.

## Logging and errors

The plugin does not log the bearer token. It redacts the configured token from network and API error messages before returning them. Structured failures may include an error code, HTTP status, message, and trace ID for troubleshooting.

## Your choices

You can stop further processing by disabling or uninstalling the plugin and removing its credential in Dify. Use Dify's controls to delete retained workflow data or logs. Omit `callback_url` to prevent callback delivery.

## Contact

For plugin questions, open an issue in the [source repository](https://github.com/AceDataCloud/Dify/tree/main/plugins/seedream) or email [office@acedata.cloud](mailto:office@acedata.cloud).
