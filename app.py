import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

def extract_transcript_details(youtube_video_url, language='hi'):
    try:
        video_id = youtube_video_url.split("v=")[-1].split("&")[0] if "v=" in youtube_video_url else youtube_video_url.split("/")[-1].split("?")[0]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            transcript = transcript_list.find_transcript([language])
        except:
            transcript = transcript_list.find_transcript(['en'])
        
        transcript_text = ""
        for segment in transcript.fetch():
            transcript_text += " " + segment["text"]

        return transcript_text

    except Exception as e:
        st.write(f"An error occurred while fetching the transcript: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("v=")[-1].split("&")[0] if "v=" in youtube_link else youtube_link.split("/")[-1].split("?")[0]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link, language='hi')

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
