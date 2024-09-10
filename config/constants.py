# Regular expression to match various YouTube URL formats
VIDEO_ID_REGEX = (
    r'(?:https?://)?'  # Match the protocol (http or https) (optional)
    r'(?:www\.)?'  # Optional www subdomain
    r'(?:youtube\.com|youtu\.be|youtube-nocookie\.com)'  # Match youtube.com or youtu.be or youtube-nocookie.com
    r'(?:.*[?&]v=|/embed/|/v/|/e/|/shorts/|/live/|/attribution_link?.*v=|/oembed\?url=.*v=|/)?'  # Match different formats or nothing
    r'([a-zA-Z0-9_-]{11})'  # Capture the 11-character video ID
)

OPENAI_SUMMARY_PROMPT = (
        "Summarize the video by providing a medium-sized description of the key points discussed. "
        "Include any important statements or quotes made by the speakers, "
        "as well as the reasoning or explanations they provide for their arguments. "
        "Ensure that the summary captures the main ideas and conclusions presented in the video. "
        "Additionally, describe the video's tone, presentation style, and target audience "
        "to help users decide whether it suits their preferences.  "
        "Focus on providing a clear overview to assist in determining whether the video is worth watching. "
        "Present the summary in "
        )


# SUMMARY_TO_SPEECH_PROMPT = ""
