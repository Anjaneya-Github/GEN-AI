import os

from dotenv import load_dotenv
from crewai import Agent

from tools import yt_tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")

blog_researcher = Agent(
    role="Senior Research Analyst",
    goal=(
       "Research the topic '{topic}' deeply using available YouTube information and turn it into a structured, evidence-based brief."
    ),
    verbose=True,
    memory=True,
    max_iter=6,
    backstory=(
       "You are an expert technical researcher who can synthesize video content, compare concepts, and extract the most relevant insights "
       "for a professional technology audience."
    ),
    tools=[yt_tool],
    allow_delegation=False,
)

blog_writer = Agent(
    role="Technical Content Writer",
    goal=(
       "Write a polished, engaging, and easy-to-follow blog article on '{topic}' using the research brief and the best available source material."
    ),
    verbose=True,
    memory=True,
    max_iter=6,
    backstory=(
       "You are a strong technical storyteller who makes complex ideas clear, practical, and compelling for a modern developer audience."
    ),
    tools=[yt_tool],
    allow_delegation=False,
)