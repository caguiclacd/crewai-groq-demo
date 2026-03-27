import html
import os
import re

import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()


def get_groq_api_key() -> str:
    # Prefer Streamlit Cloud secrets and fallback to local environment variables.
    secret_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    return (secret_key or os.getenv("GROQ_API_KEY", "")).strip()


def sanitize_topic(raw_topic: str) -> str:
    condensed = " ".join(raw_topic.split())
    allowed = re.sub(r"[^\w\s\-\.,:;!?()/]", "", condensed)
    return allowed[:300]


def sanitize_filename_fragment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return cleaned[:40] or "output"


st.set_page_config(
    page_title="CrewAI + Groq Lab",
    page_icon="🤖",
    layout="wide",
)

with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 10px 0 5px 0;'>
            <span style='font-size:42px;'>🤖</span>
            <h2 style='margin:4px 0 0 0; color:#4CAF50; font-family:monospace;'>CrewAI Lab</h2>
            <p style='margin:0; font-size:12px; color:grey;'>Powered by Groq (Free Tier)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## ⚙️ Configuration")

    model_choice = st.selectbox(
        "Groq Model",
        options=[
            "groq/llama-3.3-70b-versatile",
            "groq/llama-3.1-70b-versatile",
            "groq/mixtral-8x7b-instruct",
        ],
        index=0,
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative, Lower = more focused",
    )

    max_tokens = st.slider("Max Tokens per Agent", min_value=256, max_value=2048, value=1024, step=128)

    st.divider()
    st.markdown("### Agent Roles")
    researcher_role = st.text_input("Researcher Role", value="Research Analyst")
    writer_role = st.text_input("Writer Role", value="Content Writer")

    st.divider()
    st.caption("Free tier tip: keep max_rpm=3 to avoid rate limits")


topic = st.text_area(
    "Enter your research topic",
    placeholder="e.g. The impact of AI on software development jobs in 2026",
    height=80,
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("Run Crew", type="primary", use_container_width=True)
with col2:
    st.caption("Runs 2 agents sequentially: Researcher -> Writer")

if run_button:
    safe_topic = sanitize_topic(topic)
    if not safe_topic:
        st.warning("Please enter a valid topic before running.")
        st.stop()

    api_key = get_groq_api_key()
    if not api_key:
        st.error("GROQ_API_KEY not found. Add it in Streamlit Secrets or your local .env.")
        st.stop()

    status_col, log_col = st.columns([1, 2])

    with status_col:
        st.markdown("### Agent Status")
        researcher_status = st.empty()
        writer_status = st.empty()
        researcher_status.info("Researcher: Waiting...")
        writer_status.info("Writer: Waiting...")

    with log_col:
        st.markdown("### Live Agent Log")
        log_box = st.empty()

    log_lines = []

    def log(msg: str) -> None:
        escaped = html.escape(msg)
        log_lines.append(escaped)
        log_box.markdown(
            "<div style='background:#1e1e1e;color:#d4d4d4;padding:12px;"
            "border-radius:8px;font-family:monospace;font-size:13px;"
            f"max-height:300px;overflow-y:auto'>{'<br>'.join(log_lines[-20:])}</div>",
            unsafe_allow_html=True,
        )

    llm = LLM(
        model=model_choice,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )

    researcher_status.warning("Researcher: Running...")
    log(f"[Researcher] Starting research on: {safe_topic}")

    researcher = Agent(
        role=researcher_role,
        goal=f"Gather key facts and insights about: {safe_topic}",
        backstory="A meticulous analyst who uncovers deep insights on any subject.",
        llm=llm,
        verbose=False,
    )

    writer = Agent(
        role=writer_role,
        goal="Transform research findings into a clear, engaging summary",
        backstory="An experienced writer who makes complex topics accessible.",
        llm=llm,
        verbose=False,
    )

    research_task = Task(
        description=(
            f"Research the topic: '{safe_topic}'\n"
            "Provide exactly 5 key findings as bullet points with brief explanations."
        ),
        expected_output="A bullet-point list of 5 key findings with brief explanations.",
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "Using the research findings provided, write a concise 3-paragraph "
            "summary for a general audience. Make it engaging and informative."
        ),
        expected_output="A 3-paragraph article-style summary.",
        agent=writer,
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=False,
        max_rpm=3,
    )

    with st.spinner("Crew is working... this may take 30-60 seconds on free tier."):
        try:
            log("[Crew] Kicking off crew...")
            result = crew.kickoff()

            researcher_status.success("Researcher: Done")
            log("[Researcher] Task completed successfully.")

            writer_status.success("Writer: Done")
            log("[Writer] Task completed successfully.")
            log("[Crew] All tasks finished. Displaying results.")

        except Exception:
            researcher_status.error("An error occurred")
            st.error("Request failed. Please retry in about a minute if rate-limited.")
            st.stop()

    st.divider()
    st.markdown("## Final Output")

    result_text = str(result)
    st.text_area("Result", value=result_text, height=320)

    filename_topic = sanitize_filename_fragment(safe_topic)
    st.download_button(
        label="Download Result as .txt",
        data=result_text,
        file_name=f"crew_output_{filename_topic}.txt",
        mime="text/plain",
    )
