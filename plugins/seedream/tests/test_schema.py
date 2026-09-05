from pathlib import Path

import pytest
import yaml

TOOLS_DIR = Path(__file__).parents[1] / "tools"
SCHEMA_FILES = ("seedream_generate.yaml", "seedream_edit.yaml", "seedream_decompose.yaml")


@pytest.mark.parametrize("schema_file", SCHEMA_FILES)
def test_size_options_exclude_adaptive_and_data_remains_array(schema_file: str) -> None:
    schema = yaml.safe_load((TOOLS_DIR / schema_file).read_text())
    size_parameter = next(parameter for parameter in schema["parameters"] if parameter["name"] == "size")

    assert "adaptive" not in {option["value"] for option in size_parameter["options"]}
    assert "1.5K" in {option["value"] for option in size_parameter["options"]}
    assert schema["output_schema"]["properties"]["data"]["type"] == "array"


def test_layer_schema_and_provider_registration() -> None:
    schema = yaml.safe_load((TOOLS_DIR / "seedream_decompose.yaml").read_text())
    item = schema["output_schema"]["properties"]["data"]["items"]["properties"]
    assert {"z_index", "name", "description", "bounding_box"} <= set(item)
    provider = yaml.safe_load((TOOLS_DIR.parent / "provider" / "seedream.yaml").read_text())
    assert "tools/seedream_decompose.yaml" in provider["tools"]
