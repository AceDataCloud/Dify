from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def test_qwen_image_schema():
    manifest=yaml.safe_load((ROOT/"manifest.yaml").read_text())
    provider=yaml.safe_load((ROOT/"provider/qwen_image.yaml").read_text())
    tool=yaml.safe_load((ROOT/"tools/qwen_image.yaml").read_text())
    assert manifest["name"]=="qwen_image"
    assert provider["tools"]==["tools/qwen_image.yaml"]
    options={x["value"] for x in next(p for p in tool["parameters"] if p["name"]=="model")["options"]}
    assert options=={"qwen-image-3.0","qwen-image-3.0-pro"}
