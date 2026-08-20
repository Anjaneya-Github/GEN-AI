import os
import sys

# Patch: crewai_tools uses `pytube` internally, but pytube's channel regex is
# broken against YouTube's current page structure. `pytubefix` is the actively
# maintained fork that keeps the regexes up to date. Alias it as `pytube` so
# crewai_tools picks it up automatically.
try:
    import pytubefix
    sys.modules["pytube"] = pytubefix
except ImportError:
    pass

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from crewai_tools import YoutubeChannelSearchTool


class TopicResearchInput(BaseModel):
    query: str = Field(..., description="The topic to research for the blog.")


class FallbackYouTubeTool(BaseTool):
    name: str = "fallback_youtube_topic_research"
    description: str = (
        "Use this tool when YouTube channel indexing is unavailable. "
        "It produces a structured research brief on the topic so the agent can continue working "
        "with actionable material for a professional blog article."
    )
    args_schema: type[BaseModel] = TopicResearchInput

    def _run(self, query: str) -> str:
        cleaned_query = (query or "AI and data science").strip()
        return (
            f"YouTube channel indexing is unavailable in this environment, so create a practical research brief for '{cleaned_query}'.\n\n"
            f"1. Executive summary: Explain the topic in plain language and highlight why it matters today.\n"
            f"2. Key concepts: Define the core terms, differences, and key misconceptions.\n"
            f"3. Real-world use cases: Show where this topic matters in industry, products, and decision-making.\n"
            f"4. Comparison and trade-offs: Clarify how it differs from adjacent concepts using examples.\n"
            f"5. Practical takeaways: Give 3-5 actionable lessons for a technical audience.\n"
            f"6. Blog outline: Propose a clear title, introduction, 4-5 section structure, and conclusion.\n\n"
            f"Use this brief to write a polished, beginner-friendly but expert-level article."
        )


def build_yt_tool():
    channel_handle = os.getenv("YOUTUBE_CHANNEL_HANDLE", "@krishnaik06")

    try:
        return YoutubeChannelSearchTool(youtube_channel_handle=channel_handle)
    except Exception:
        return FallbackYouTubeTool()


yt_tool = build_yt_tool()

