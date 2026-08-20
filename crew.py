from crewai import Crew, Process

from agents import blog_researcher, blog_writer
from tasks import research_task, write_task

DEFAULT_TOPIC = "AI VS ML VS DL vs Data Science"

crew = Crew(
   agents=[blog_researcher, blog_writer],
   tasks=[research_task, write_task],
   process=Process.sequential,
   memory=True,
   cache=True,
   max_rpm=100,
   share_crew=True,
)

if __name__ == "__main__":
   print("\n=== Starting CrewAI blog generation ===")
   print(f"Topic: {DEFAULT_TOPIC}\n")
   result = crew.kickoff(inputs={"topic": DEFAULT_TOPIC})
   print("\n=== Final output ===")
   print(result)
