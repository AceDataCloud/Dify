from collections.abc import Mapping

from httpx import Timeout


class _CommonAceDataCloud:

    def _to_credential_kwargs(self, credentials: Mapping) -> dict:
        """
        Transform credentials to kwargs for model instance

        :param credentials:
        :return:
        """
        credentials_kwargs = {
            "api_key": credentials['api_key'],
            "timeout": Timeout(315.0, read=300.0, write=10.0, connect=5.0),
            "max_retries": 1,
        }

        credentials_kwargs["base_url"] = 'https://api.acedatacloud.com/openai/'

        return credentials_kwargs
