from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re


def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Could not extract video ID from URL: {url}")
    return match.group(1)


def get_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    try:
        ytt = YouTubeTranscriptApi()
        chunks = ytt.fetch(video_id)
        return " ".join(chunk.text for chunk in chunks)
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript found for this video.")
