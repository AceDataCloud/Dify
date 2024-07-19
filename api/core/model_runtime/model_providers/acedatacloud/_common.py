from collections.abc import Mapping
from httpx import Timeout
import logging

logger = logging.getLogger(__name__)


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

        credentials_kwargs["base_url"] = 'https://api.acedata.cloud/openai/'
        # credentials_kwargs["base_model_name"] = 'gpt-3.5-turbo'
        logger.debug(f"credentials_kwargs: {credentials}")
        return credentials_kwargs
