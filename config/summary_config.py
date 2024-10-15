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
        "v5": ConfigVersion(
            version="v5",
            prompt = (
                "Provide a 100-150 word summary of the video, focusing on **insights** that are relevant to its genre. "
                "Structure the summary with the following adaptable sections:\n"
                "1. **Main Theme or Focus**: Identify the overarching topic, storyline, or focus (e.g., a dramatic arc, match highlights, news events).\n"
                "2. **Core Insights or Highlights**: What are the unique takeaways or memorable moments? "
                "For example:\n"
                "   - In drama: Character developments, emotional turning points, or themes explored.\n"
                "   - In sports: Key plays, standout performances, or game-changing moments.\n"
                "   - In news/documentaries: New information, perspectives, or key findings.\n"
                "3. **Supporting Details**: Include any context, reasoning, or background that helps understand these insights or moments better.\n"
                "4. **Notable Quotes, Moments, or Actions**: Capture anything that stood out—whether it’s a quote, emotional scene, or decisive action.\n"
                "5. **Conclusion or Implications**: Summarize the takeaway—does it offer reflection, excitement, lessons, or future directions?\n"
                "Ensure the summary provides a meaningful overview, tailored to the genre, to help the reader decide whether the video is worth watching."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        "v4": ConfigVersion(
            version="v4",
            prompt=(
                "Summarize the video by providing a 100-150 words description of the key points discussed. "
                "Include any important statements or quotes made by the speakers, "
                "as well as the reasoning or explanations they provide for their arguments. "
                "Ensure that the summary captures the main ideas and conclusions presented in the video. "
                "Focus on providing a clear overview to assist in determining whether the video is worth watching."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        "v3": ConfigVersion(
            version="v3",
            prompt = (
                "Provide a structured summary of the video in 100-150 words, organized as follows:\n"
                "1. Overview (1-2 sentences):\n"
                "   • Briefly describe the video's main topic and format\n"
                "2. Key Points (3-4 bullet points):\n"
                "   • List the main ideas and conclusions presented\n"
                "   • Include at least one direct quote from a speaker\n"
                "3. Analysis (2-3 sentences):\n"
                "   • Explain the logic behind key arguments\n"
                "   • Comment on the presentation style and target audience\n"
                "4. Final Verdict (1 sentence):\n"
                "   • Recommend whether the video is worth watching and for whom\n"
                "Ensure the summary provides a clear, concise overview to help users quickly decide if the content meets their needs."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        "v2": ConfigVersion(
            version="v2",
            prompt = (
                "Provide a structured summary of the video in 100-150 words, organized as follows:\n"
                "1. Key Points (3-4 bullet points):\n"
                "   • List the main ideas and conclusions presented\n"
                "   • Include important quotes or statements from speakers\n"
                "2. Arguments and Reasoning:\n"
                "   • Briefly explain the logic behind key arguments\n"
                "3. Final Verdict:\n"
                "   • Conclude with a one-sentence recommendation on whether the video is worth watching\n"
                "Ensure the summary provides a clear overview to help users decide if the content meets their needs."
            ),
            model="gpt-4o-mini",
            max_tokens=125000
        ),
        "v1": ConfigVersion(
            version="v1",
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

    CURRENT_VERSION = "v5"

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