import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load .env file so GROQ_API_KEY is available
load_dotenv()

# --- 1. Configure the LLM (Groq + LLaMA 3) ---
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.7,
    max_completion_tokens=1024
)

# --- 2. Define Agents (each has a role, goal, backstory) ---
researcher = Agent(
    role="Research Analyst",
    goal="Gather key facts and insights on a given topic",
    backstory="A curious analyst who digs deep into any subject with precision.",
    llm=llm,
    verbose=True  # Shows the agent's thinking process
)

writer = Agent(
    role="Content Writer",
    goal="Turn research notes into a clear, engaging summary",
    backstory="An experienced writer who makes complex topics easy to understand.",
    llm=llm,
    verbose=True
)

# --- 3. Define Tasks (what each agent should do) ---
research_task = Task(
    description="Research the topic: 'The impact of AI on software development jobs in 2025'. List 5 key findings.",
    expected_output="A bullet-point list of 5 key findings with brief explanations.",
    agent=researcher
)

writing_task = Task(
    description="Using the research findings, write a short 3-paragraph summary for a general audience.",
    expected_output="A 3-paragraph article-style summary.",
    agent=writer,
    dependencies=[research_task]  # Runs AFTER the research task finishes
)

# --- 4. Assemble the Crew and Run ---
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True,
    max_rpm=3  # IMPORTANT: Stays within Groq's free tier rate limits
)

result = crew.kickoff()
print("\n===== FINAL OUTPUT =====")
print(result)
