from typing import Dict
from dataclasses import dataclass

@dataclass
class ConfigVersion:
    version: str
    prompt: str
    model: str
    max_tokens: int

class SummaryConfig:
    VERSIONS: Dict[str, ConfigVersion] = {
        "v1.0": ConfigVersion(
            version="v1.0",
            prompt=(
                "Provide a brief structured summary of the video in 50-150 words, focusing on valuable insights aligned with its genre. "
                "Include any important statements or quotes made by the speakers, "
                "as well as the reasoning or explanations they provide for their arguments. "
                "Ensure that the summary captures the main ideas and conclusions presented in the video. "
                "Focus on providing a clear overview to assist in determining whether the video is worth watching."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        "v1.0-dev": ConfigVersion(
            version="v1.0-dev",
            prompt=(
                "Summarize the video by providing a medium-sized description of the key points discussed. "
                "Include any important statements or quotes made by the speakers, "
                "as well as the reasoning or explanations they provide for their arguments. "
                "Ensure that the summary captures the main ideas and conclusions presented in the video. "
                "Additionally, describe the video's tone, presentation style, and target audience "
                "to help users decide whether it suits their preferences. "
                "Focus on providing a clear overview to assist in determining whether the video is worth watching."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        # Add more versions here as needed
    }

    CURRENT_VERSION = "v1.0"

    @classmethod
    def set_current_version(cls, version: str):
        if version in cls.VERSIONS:
            cls.CURRENT_VERSION = version
        else:
            raise ValueError(f"Version {version} not found in config versions.")

    @classmethod
    def get_version(cls) -> str:
        return cls.CURRENT_VERSION

    @classmethod
    def get_prompt(cls) -> str:
        return cls.VERSIONS[cls.CURRENT_VERSION].prompt

    @classmethod
    def get_model(cls) -> str:
        return cls.VERSIONS[cls.CURRENT_VERSION].model

    @classmethod
    def get_max_tokens(cls) -> int:
        return cls.VERSIONS[cls.CURRENT_VERSION].max_tokens