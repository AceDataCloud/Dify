import os

from core.model_runtime.model_providers.acedatacloud.text_embedding.text_embedding import AceDataCloudTextEmbeddingModel


def test_get_num_tokens():
    model = AceDataCloudTextEmbeddingModel()

    num_tokens = model.get_num_tokens(
        model='text-embedding-ada-002',
        credentials={
            'api_key': os.environ.get('ACEDATACLOUD_API_KEY'),
        },
        texts=[
            "hello",
            "world"
        ]
    )
    assert num_tokens == 2
