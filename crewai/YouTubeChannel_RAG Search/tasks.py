from crewai import Task

from agents import blog_researcher, blog_writer
from tools import yt_tool

research_task = Task(
    description=(
        "Research the topic '{topic}' thoroughly. Use the available YouTube material and any fallback knowledge. "
        "Identify the main ideas, important definitions, practical examples, common misconceptions, and the difference between related concepts. "
        "Produce a clear, structured research brief with an executive summary, major themes, examples, and a suggested article outline."
    ),
    expected_output=(
        "A structured research brief on '{topic}' with: a concise executive summary, key concepts, real-world use cases, comparison points, "
        "takeaways, and an article outline."
    ),
    tools=[yt_tool],
    agent=blog_researcher,
)

write_task = Task(
    description=(
        "Write a polished blog article on '{topic}' using the research brief. The article should be engaging, technically accurate, and accessible to a curious developer audience. "
        "Include a strong introduction, clear section headings, useful examples, and a concise conclusion. "
        "Write in markdown with a professional tone and avoid fluff."
    ),
    expected_output=(
        "A full markdown blog article on '{topic}' in a clear, readable, publication-ready style with headings, bullet points, and examples."
    ),
    tools=[yt_tool],
    agent=blog_writer,
    async_execution=False,
    output_file="new-blog-post.md",
)

