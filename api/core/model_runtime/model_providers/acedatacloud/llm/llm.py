from core.model_runtime.model_providers.openai.llm.llm import OpenAILargeLanguageModel
from core.model_runtime.model_providers.acedatacloud._common import _CommonAceDataCloud


class AceDataCloudLargeLanguageModel(_CommonAceDataCloud, OpenAILargeLanguageModel):
    pass
