from enum import StrEnum


class PipelineTemplateType(StrEnum):
    REMOTE = "remote"
    DATABASE = "database"
    CUSTOMIZED = "customized"
    BUILT_IN = "builtin"
