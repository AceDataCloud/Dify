from core.model_runtime.model_providers.acedatacloud._common import _CommonAceDataCloud
from core.model_runtime.model_providers.openai.text_embedding.text_embedding import OpenAITextEmbeddingModel


class AceDataCloudTextEmbeddingModel(_CommonAceDataCloud, OpenAITextEmbeddingModel):
    pass
