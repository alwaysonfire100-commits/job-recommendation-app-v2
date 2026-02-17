import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from helper import extract_text_from_pdf
from job_api import fetch_linkedin_jobs, fetch_naukri_jobs

# ---------------------------
# Load Environment Variables
# ---------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. Add it in .env or Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer & Job Recommender")
st.markdown("Upload your resume and get AI insights + real job recommendations.")

# ---------------------------
# File Upload
# ---------------------------
uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

if uploaded_file:

    # Extract Resume Text
    with st.spinner("Extracting resume text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text.startswith("Error"):
        st.error(resume_text)
        st.stop()

    # ---------------------------
    # Resume Summary
    # ---------------------------
    with st.spinner("Generating resume summary..."):
        summary_prompt = f"""
        Summarize this resume professionally in 5-6 lines:

        {resume_text}
        """

        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": summary_prompt}],
        ).choices[0].message.content

    # ---------------------------
    # Skill Gaps
    # ---------------------------
    with st.spinner("Finding skill gaps..."):
        gap_prompt = f"""
        Identify missing skills and improvement areas 
        for tech/data roles based on this resume:

        {resume_text}
        """

        gaps = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": gap_prompt}],
        ).choices[0].message.content

    # ---------------------------
    # Roadmap
    # ---------------------------
    with st.spinner("Creating roadmap..."):
        roadmap_prompt = f"""
        Create a structured 3-6 month roadmap 
        to improve skills and get hired in tech/data field:

        {resume_text}
        """

        roadmap = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": roadmap_prompt}],
        ).choices[0].message.content

    # ---------------------------
    # Job Keywords
    # ---------------------------
    keyword_prompt = f"""
    Extract exactly 5 short job search keywords.
    Return only comma separated words.

    {resume_text}
    """

    keywords = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": keyword_prompt}],
    ).choices[0].message.content

    search_keywords = keywords.replace("\n", "").strip()

    # ---------------------------
    # Display Results
    # ---------------------------
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.write(summary)

    st.markdown("---")
    st.header("🛠️ Skill Gaps")
    st.write(gaps)

    st.markdown("---")
    st.header("🚀 3–6 Month Roadmap")
    st.write(roadmap)

    st.success("✅ Analysis Completed Successfully!")

    # ---------------------------
    # Job Recommendation Button
    # ---------------------------
    if st.button("🔎 Get Job Recommendations"):

        st.info(f"Searching jobs for: {search_keywords}")

        with st.spinner("Fetching LinkedIn jobs..."):
            linkedin_jobs = fetch_linkedin_jobs(search_keywords, rows=15)

        with st.spinner("Fetching Naukri jobs..."):
            naukri_jobs = fetch_naukri_jobs(search_keywords, rows=15)

        # ---------------------------
        # LinkedIn Jobs
        # ---------------------------
        st.markdown("---")
        st.header("💼 LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(f"**{job.get('title')}**")
                st.markdown(f"🏢 {job.get('companyName')}")
                st.markdown(f"📍 {job.get('location')}")
                if job.get("link"):
                    st.markdown(f"[View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

        # ---------------------------
        # Naukri Jobs
        # ---------------------------
        st.header("💼 Naukri Jobs (India)")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(f"**{job.get('title')}**")
                st.markdown(f"🏢 {job.get('companyName')}")
                st.markdown(f"📍 {job.get('location')}")
                if job.get("url"):
                    st.markdown(f"[View Job]({job.get('url')})")
                st.markdown("---")
        else:
            st.warning("No Naukri jobs found.")

