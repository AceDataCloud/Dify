import os
import pytest
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.acedatacloud.llm.llm import AcdDataCloudLargeLanguageModel
from core.model_runtime.entities.message_entities import (
    UserPromptMessage,
)
from core.model_runtime.entities.llm_entities import LLMResult


def test_validate_credentials():
    model = AcdDataCloudLargeLanguageModel()

    with pytest.raises(CredentialsValidateFailedError):
        model.validate_credentials(
            model='gpt-3.5-turbo',
            credentials={
                'api_key': 'invalid_key',
            }
        )

    model.validate_credentials(
        model='gpt-3.5-turbo',
        credentials={
            'api_key': os.environ.get('ACEDATACLOUD_API_KEY')
        }
    )


def test_invoke_model():
    model = AcdDataCloudLargeLanguageModel()

    response = model.invoke(
        model='gpt-3.5-turbo',
        credentials={
            'api_key': os.environ.get('ACEDATACLOUD_API_KEY'),
        },
        prompt_messages=[
            UserPromptMessage(
                content='Hello World!'
            )
        ],
        model_parameters={
            'temperature': 0.0,
            'max_tokens': 1
        },
        stream=False,
        user="abc-123"
    )

    assert isinstance(response, LLMResult)
    assert len(response.message.content) > 0
