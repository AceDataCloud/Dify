from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.acedata_client import (
    AceDataSunoClient,
    AceDataSunoError,
    parse_optional_float,
)


class SunoGenerateAudiosTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        action = tool_parameters.get("action")
        if not isinstance(action, str) or not action.strip():
            raise ValueError("`action` is required.")
        action = action.strip()

        prompt = tool_parameters.get("prompt")
        prompt = prompt.strip() if isinstance(prompt, str) and prompt.strip() else None

        model = tool_parameters.get("model")
        model = model.strip() if isinstance(model, str) and model.strip() else None

        custom = tool_parameters.get("custom")
        if custom is not None and not isinstance(custom, bool):
            raise ValueError("`custom` must be a boolean.")

        instrumental = tool_parameters.get("instrumental")
        if instrumental is not None and not isinstance(instrumental, bool):
            raise ValueError("`instrumental` must be a boolean.")

        lyric = tool_parameters.get("lyric")
        lyric = lyric.strip() if isinstance(lyric, str) and lyric.strip() else None

        lyric_prompt = tool_parameters.get("lyric_prompt")
        lyric_prompt = (
            lyric_prompt.strip()
            if isinstance(lyric_prompt, str) and lyric_prompt.strip()
            else None
        )

        title = tool_parameters.get("title")
        title = title.strip() if isinstance(title, str) and title.strip() else None

        style = tool_parameters.get("style")
        style = style.strip() if isinstance(style, str) and style.strip() else None

        negative_tags = tool_parameters.get("negative_tags")
        negative_tags = (
            negative_tags.strip()
            if isinstance(negative_tags, str) and negative_tags.strip()
            else None
        )

        audio_id = tool_parameters.get("audio_id")
        audio_id = (
            audio_id.strip() if isinstance(audio_id, str) and audio_id.strip() else None
        )

        audio_urls_raw = tool_parameters.get("audio_urls")
        audio_urls: list[str] | None = None
        if isinstance(audio_urls_raw, str) and audio_urls_raw.strip():
            audio_urls = [u.strip() for u in audio_urls_raw.split(",") if u.strip()]
        elif isinstance(audio_urls_raw, list):
            audio_urls = [str(u).strip() for u in audio_urls_raw if str(u).strip()]
        if audio_urls is not None and not audio_urls:
            audio_urls = None

        continue_at = parse_optional_float(
            tool_parameters.get("continue_at"), field="continue_at"
        )
        audio_weight = parse_optional_float(
            tool_parameters.get("audio_weight"), field="audio_weight"
        )

        persona_id = tool_parameters.get("persona_id")
        persona_id = (
            persona_id.strip()
            if isinstance(persona_id, str) and persona_id.strip()
            else None
        )

        vocal_gender = tool_parameters.get("vocal_gender")
        vocal_gender = (
            vocal_gender.strip()
            if isinstance(vocal_gender, str) and vocal_gender.strip()
            else None
        )
        if vocal_gender is not None and vocal_gender not in {"f", "m"}:
            raise ValueError("`vocal_gender` must be 'f' or 'm'.")

        variation_category = tool_parameters.get("variation_category")
        variation_category = (
            variation_category.strip()
            if isinstance(variation_category, str) and variation_category.strip()
            else None
        )
        if variation_category is not None and variation_category not in {
            "high",
            "normal",
            "subtle",
        }:
            raise ValueError(
                "`variation_category` must be 'high', 'normal', or 'subtle'."
            )

        weirdness = parse_optional_float(
            tool_parameters.get("weirdness"), field="weirdness"
        )
        style_influence = parse_optional_float(
            tool_parameters.get("style_influence"), field="style_influence"
        )

        # Dify has no integer parameter type, so a whole number arrives as a float.
        # Narrow it back to int; the API owns every other rule about the value.
        duration = parse_optional_float(
            tool_parameters.get("duration"), field="duration"
        )
        if duration is not None and duration.is_integer():
            duration = int(duration)

        callback_url = tool_parameters.get("callback_url")
        callback_url = (
            callback_url.strip()
            if isinstance(callback_url, str) and callback_url.strip()
            else None
        )

        if action == "inspo":
            if not audio_urls or not 1 <= len(audio_urls) <= 4:
                raise ValueError(
                    "`audio_urls` must contain 1 to 4 reference audio URLs when action is inspo."
                )
        elif custom is True:
            if not lyric and not lyric_prompt and not instrumental:
                raise ValueError(
                    "When `custom` is true, provide `lyric` or `lyric_prompt` (unless instrumental)."
                )
        else:
            if not prompt:
                raise ValueError("`prompt` is required when `custom` is false.")

        actions_requiring_audio_id = {
            "extend",
            "upload_extend",
            "cover",
            "upload_cover",
            "stems",
            "all_stems",
            "concat",
            "remaster",
            "replace_section",
            "mashup",
        }
        if action in actions_requiring_audio_id and not audio_id:
            raise ValueError(f"`audio_id` is required when action is {action}.")

        payload: dict[str, Any] = {"action": action}
        if prompt:
            payload["prompt"] = prompt
        if model:
            payload["model"] = model
        if custom is not None:
            payload["custom"] = custom
        if instrumental is not None:
            payload["instrumental"] = instrumental
        if lyric:
            payload["lyric"] = lyric
        if lyric_prompt:
            payload["lyric_prompt"] = lyric_prompt
        if title:
            payload["title"] = title
        if style:
            payload["style"] = style
        if negative_tags:
            payload["negative_tags"] = negative_tags
        if audio_id:
            payload["audio_id"] = audio_id
        if audio_urls:
            payload["audio_urls"] = audio_urls
        if continue_at is not None:
            payload["continue_at"] = continue_at
        if audio_weight is not None:
            payload["audio_weight"] = audio_weight
        if persona_id:
            payload["persona_id"] = persona_id
        if vocal_gender:
            payload["vocal_gender"] = vocal_gender
        if variation_category:
            payload["variation_category"] = variation_category
        if weirdness is not None:
            payload["weirdness"] = weirdness
        if style_influence is not None:
            payload["style_influence"] = style_influence
        if duration is not None:
            payload["duration"] = duration
        if callback_url:
            payload["callback_url"] = callback_url
        if tool_parameters.get("async"):
            payload["async"] = True

        client = AceDataSunoClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_audios(payload=payload, timeout_s=1800)
        except AceDataSunoError as e:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message(
                "error", {"code": e.code, "message": e.message}
            )
            yield self.create_variable_message("trace_id", e.trace_id)
            return

        for image_url in result.image_urls:
            yield self.create_image_message(image_url)

        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
