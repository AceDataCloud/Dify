from core.model_runtime.model_providers.openai.text_embedding.text_embedding import OpenAITextEmbeddingModel
from core.model_runtime.model_providers.acedatacloud._common import _CommonAceDataCloud


class AceDataCloudTextEmbeddingModel(_CommonAceDataCloud, OpenAITextEmbeddingModel):
    pass
