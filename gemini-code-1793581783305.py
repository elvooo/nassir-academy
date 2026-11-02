import os
import streamlit as st
from google import genai
from pypdf import PdfReader

# Page Configuration for Mobile & Laptop Responsiveness
st.set_page_config(
    page_title="Nassir Academy Classes", page_icon="🎓", layout="centered"
)

st.title("🎓 Nassir Academy Classes")
st.subheader("AI Agent: Dr. Nassir Ibrahim")
st.markdown(
    "Welcome to the official MAN4049 interactive assistant. Ask any questions"
    " about your Excel labs, data processing, pivot tables, and formulas!"
)

# Sidebar for Gemini API Key configuration
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

if not api_key:
  st.warning(
      "Please enter your Google Gemini API key in the sidebar to start chatting."
  )
  st.stop()

client = genai.Client(api_key=api_key)


# Load and extract text from your lesson PDFs
@st.cache_resource
def load_lesson_documentation():
  pdf_files = [
      "Week1LabData ProcessingMAN4049.pdf",
      "Week 2 LabCondensed_261101_232537.pdf",
      "Week 3 - Lab 31  32 PDF - Sorting, Filtering  Su_261026_203810.pdf",
      "MAN4049_Week5_LabPDF_261026_215928.pdf",
  ]
  combined_text = ""
  for file in pdf_files:
    if os.path.exists(file):
      reader = PdfReader(file)
      for page in reader.pages:
        text = page.extract_text()
        if text:
          combined_text += text + "\n"
  return combined_text


lesson_context = load_lesson_documentation()

# System Instructions defining the Agent's persona
system_instruction = (
    "You are Dr. Nassir Ibrahim, module leader for MAN4049[cite: 10]. Your"
    " purpose is to help students understand data processing, Excel charts,"
    " PivotTables, sorting, filtering, and formulas based strictly on the"
    " provided course notes. Always be encouraging, clear, and educational."
)

# Chat History State
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Input Handling
if user_query := st.chat_input(
    "Ask Dr. Nassir Ibrahim a question about your labs..."
):
  st.session_state.messages.append({"role": "user", "content": user_query})
  with st.chat_message("user"):
    st.markdown(user_query)

  with st.chat_message("assistant"):
    with st.spinner("Reviewing lesson documents..."):
      # Construct Agentic RAG Prompt
      prompt = f"""
            {system_instruction}
            
            LESSON DOCUMENTATION / KNOWLEDGE BASE:
            {lesson_context[:30000]}
            
            STUDENT QUESTION: {user_query}
            """

      response = client.models.generate_content(
          model="gemini-2.5-flash", contents=prompt
      )
      answer = response.text
      st.markdown(answer)
      st.session_state.messages.append({"role": "assistant", "content": answer})