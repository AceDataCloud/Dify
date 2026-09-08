# Privacy

This policy describes the data flow of the Ace Data Cloud SERP plugin for Dify.

## Data processed

When the tool runs, the plugin processes:

- the Ace Data Cloud bearer token configured in Dify;
- the search query;
- optional search type, country, language, date range, result count, and page number;
- the structured search response, error details, and trace ID returned by the API.

Search queries may contain personal or confidential information. Do not submit data that you are not authorized to process.

## Data transfer

The plugin sends the query and provided search parameters over HTTPS only to the fixed endpoint `https://api.acedata.cloud/serp/google`. The bearer token is sent only in the `Authorization` header. The plugin does not accept an alternate API host or arbitrary destination URL.

The API response is returned to the Dify workflow. The plugin does not send data to advertising or analytics services and contains no telemetry code.

## Storage and retention

The plugin does not write queries, responses, or credentials to local files or its own database. Dify controls how plugin credentials, workflow inputs, outputs, and execution logs are stored and retained. Data processed by Ace Data Cloud is subject to the [Ace Data Cloud Privacy Policy](https://platform.acedata.cloud/privacy).

## Logging and errors

The plugin does not log the bearer token. Structured API errors may return an error code, message, HTTP status, and trace ID to the Dify workflow for troubleshooting.

## Your choices

You can stop further processing by disabling or uninstalling the plugin and removing its credential in Dify. Use Dify's controls to delete retained workflow data or logs.

## Contact

For plugin questions, open an issue in the [source repository](https://github.com/AceDataCloud/Dify/tree/main/plugins/serp) or email [office@acedata.cloud](mailto:office@acedata.cloud).
