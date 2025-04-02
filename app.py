import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the Gemini AI API
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Missing Google API Key. Please set GOOGLE_API_KEY in .env file.")

# Prompt for summarization
PROMPT_TEMPLATE = """You are a YouTube video summarizer. 
You will be taking the transcript text and summarizing the entire video, 
providing the important summary in bullet points within 250 words.

Here is the transcript:
"""

def extract_transcript_details(youtube_video_url, language='hi'):
    """Fetches the YouTube video transcript."""
    try:
        video_id = youtube_video_url.split("v=")[-1].split("&")[0] if "v=" in youtube_video_url else youtube_video_url.split("/")[-1].split("?")[0]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_transcript([language])
        except:
            transcript = transcript_list.find_transcript(['en'])  # Fallback to English if Hindi isn't available

        transcript_text = " ".join(segment["text"] for segment in transcript.fetch())
        return transcript_text
    except Exception as e:
        return None  # Return None so we can prompt for manual transcript

def generate_gemini_content(transcript_text):
    """Generates a summarized response using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(PROMPT_TEMPLATE + transcript_text)
        return response.text if response else "No summary available."
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit App UI
st.title("📺 YouTube Video Summarizer")

youtube_link = st.text_input("Enter YouTube Video Link:")
manual_transcript = None

if youtube_link:
    video_id = youtube_link.split("v=")[-1].split("&")[0] if "v=" in youtube_link else youtube_link.split("/")[-1].split("?")[0]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Summary"):
    transcript_text = extract_transcript_details(youtube_link, language='hi')
    
    if not transcript_text:
        st.warning("Failed to fetch transcript. YouTube may have blocked requests from this server.")
        manual_transcript = st.text_area("Paste the transcript manually (if available):")
    
    if transcript_text or manual_transcript:
        summary = generate_gemini_content(transcript_text or manual_transcript)
        if summary:
            st.markdown("## 📌 Summary:")
            st.write(summary)
        else:
            st.warning("Failed to generate a summary. Please try again.")
