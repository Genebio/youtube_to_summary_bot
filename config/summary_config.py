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
                "Provide a concise 100-150 word summary of the video, focusing on **valuable insights** aligned with its genre. "
                "Organize the summary using the following sections:\n"
                "1. **Theme or Focus**: Briefly describe the core topic, storyline, or purpose of the video (e.g., dramatic arc, match highlights, or breaking news).\n"
                "2. **Key Insights or Memorable Moments**: Highlight the most significant elements unique to the video. Depending on the genre, this might include:\n"
                "   - Drama: Emotional peaks, character transformations, or themes explored.\n"
                "   - Sports: Critical plays, standout performances, or turning points.\n"
                "   - News/Documentaries: New perspectives, discoveries, or revelations.\n"
                "3. **Context or Reasoning**: Provide background or explanations that enhance understanding of the key insights.\n"
                "4. **Impactful Details**: Capture any remarkable quotes, actions, or events that left a lasting impression.\n"
                "5. **Takeaways or Implications**: Summarize the broader message, excitement, or lesson, offering a reason to engage with the video.\n"
                "Ensure the summary flows smoothly, without unnecessary repetition, and provides a meaningful snapshot to help the reader assess the video’s relevance."
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