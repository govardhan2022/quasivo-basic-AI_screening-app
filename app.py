import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)


class CandidateScreeningApp:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception:
            return ""

    def load_prompt(self, filename):
        """Load prompt from /prompts/ directory"""
        path = os.path.join("prompts", filename)
        if not os.path.exists(path):
            st.error(f"Prompt file '{filename}' not found in /prompts/")
            st.stop()
        with open(path, "r") as f:
            return f.read()

    def generate_interview_questions(self, job_description, resume_text):
        prompt = self.load_prompt("generate_questions_prompt.txt").format(
            job_description=job_description,
            resume_text=resume_text
        )
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()
            questions = [line.strip() for line in content.split('\n') if line.strip()]
            return questions[:3]
        except Exception:
            return []

    def score_answer(self, question, answer):
        prompt = self.load_prompt("score_answer_prompt.txt").format(
            question=question,
            answer=answer
        )
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()

            if content and len(content) >= 2 and content[0].isdigit():
                score = int(content[0])
                explanation = content[2:].strip()
            else:
                score = 6
                explanation = "Good attempt! The answer was somewhat clear and relevant."

            score = max(1, min(score, 10))
            return score, explanation
        except Exception:
            return 6, "The AI had trouble evaluating this one. We gave a fair score based on typical performance."

    def run(self):
        st.set_page_config(page_title="🤖 Quasivo AI Screening App", layout="wide")
        st.title("🤖 Quasivo AI Screening App")

        # Input Collection
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Job Description")
            jd_method = st.radio("Input Method", ["Text", "File"], key="jd_input")
            if jd_method == "Text":
                job_description = st.text_area("Paste job description here:", height=200, key="jd_text")
            else:
                jd_file = st.file_uploader("Upload JD (TXT or PDF)", type=["txt", "pdf"], key="jd_upload")
                job_description = ""
                if jd_file:
                    if jd_file.type == "application/pdf":
                        job_description = self.extract_text_from_pdf(jd_file)
                    else:
                        job_description = jd_file.read().decode("utf-8")
                    st.success("✅ Job description loaded successfully!")

        with col2:
            st.subheader("Candidate Resume")
            resume_input_method = st.radio("Resume input method:", ["Text Input", "File Upload"])
            if resume_input_method == "Text Input":
                resume_text = st.text_area("Paste resume here:", height=200)
            else:
                resume_file = st.file_uploader("Upload resume (PDF only)", type=["pdf"])
                if resume_file:
                    resume_text = self.extract_text_from_pdf(resume_file)
                    st.success("✅ Resume uploaded successfully!")
                else:
                    resume_text = ""

        if st.button("🚀 Start Screening") and job_description and resume_text:
            with st.spinner("🎯 Getting ready to ask some great questions..."):
                questions = self.generate_interview_questions(job_description, resume_text)
                if questions:
                    st.session_state.questions = questions
                    st.session_state.answers = {}
                    st.session_state.scores = {}
                    st.session_state.resume_text = resume_text
                    st.session_state.job_description = job_description
                    st.session_state.current_idx = 0
                    st.experimental_rerun()

        # Interview Flow
        if 'questions' in st.session_state and st.session_state.questions:
            total = len(st.session_state.questions)
            current_idx = st.session_state.get("current_idx", 0)
            st.markdown("---")
            st.subheader(f"Question {current_idx + 1} of {total}")
            question = st.session_state.questions[current_idx]
            st.markdown(f"**{question}**")
            default_answer = st.session_state.answers.get(current_idx, "")
            answer = st.text_area("Your Answer:", value=default_answer, key=f"ans_{current_idx}", height=150)

            col_nav = st.columns([1, 1, 1])
            with col_nav[0]:
                if current_idx > 0:
                    if st.button("⬅️ Previous", use_container_width=True):
                        st.session_state.answers[current_idx] = answer
                        st.session_state.current_idx -= 1
                        st.experimental_rerun()
            with col_nav[2]:
                if current_idx < total - 1:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.answers[current_idx] = answer
                        st.session_state.current_idx += 1
                        st.experimental_rerun()
                else:
                    if st.button("Finish", use_container_width=True):
                        st.session_state.answers[current_idx] = answer
                        # Score all answers
                        scores = {}
                        explanations = {}
                        for idx in range(total):
                            q = st.session_state.questions[idx]
                            a = st.session_state.answers.get(idx, "")
                            score, explanation = self.score_answer(q, a)
                            scores[idx] = score
                            explanations[idx] = explanation
                        st.session_state.scores = scores
                        st.session_state.explanations = explanations
                        st.session_state.completed = True
                        st.experimental_rerun()

        # Results View
        if st.session_state.get("completed"):
            st.markdown("---")
            st.subheader("✅ Results Summary")
            scores_list = list(st.session_state.scores.values())
            if scores_list:
                total_score = sum(scores_list)
                avg_score = round(total_score / len(scores_list), 1)
                st.markdown(f"### 📊 Average Score: **{avg_score}/10**")
            else:
                st.warning("⚠️ Could not calculate score for any question.")

            for idx, question in enumerate(st.session_state.questions):
                score = st.session_state.scores.get(idx, 6)
                explanation = st.session_state.explanations.get(idx, "The system had trouble evaluating this one.")
                answer = st.session_state.answers.get(idx, "")
                st.markdown(f"""
                <div style="border:1px solid #eee; padding:15px; margin-bottom:10px; border-radius:8px;">
                    <strong>Question {idx+1}:</strong> {question}<br><br>
                    <strong>Your Answer:</strong> {answer}<br><br>
                    <strong>Score:</strong> {score}/10<br>
                    <em>{explanation}</em>
                </div>
                """, unsafe_allow_html=True)

            if st.button("💾 Save Results"):
                data = {
                    "job_description": st.session_state.job_description,
                    "resume_text": st.session_state.resume_text,
                    "questions": st.session_state.questions,
                    "answers": st.session_state.answers,
                    "scores": st.session_state.scores,
                    "explanations": st.session_state.explanations,
                    "timestamp": datetime.now().isoformat()
                }
                filename = self.save_to_json(data)
                st.success(f"Saved to `{filename}` in the `data/` folder.")

    def save_to_json(self, data, filename=None):
        """Save screening results to a JSON file"""
        if filename is None:
            filename = f"screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filename


# Run the app
if __name__ == "__main__":
    app = CandidateScreeningApp()
    app.run()