# 🤖 Quasivo AI Screening App

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/govardhan2022/quasivo-basic-AI_screening) 
[![License](https://img.shields.io/github/license/yourusername/quasivo-basic-AI_screening)](LICENSE) 
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/framework-streamlit-orange)](https://streamlit.io) 

A Streamlit-based interview assistant powered by **Google Gemini API**, designed to generate interview questions and evaluate candidate responses using AI.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [How to Run the App Locally](#how-to-run-the-app-locally)
4. [Folder Structure and Data Storage](#folder-structure-and-data-storage)

---

## 🧠 Overview

This app helps hiring teams screen job candidates by:
- Generating tailored interview questions based on a job description and resume.
- Evaluating answers using Google Gemini's powerful LLM capabilities.
- Providing instant feedback and scoring (1–10) per question.

Perfect for recruiters, HR teams, and technical leads who want to streamline their screening process with AI.

---

## 🌟 Features

- ✅ Upload PDF resumes and job descriptions
- 💬 Generate 3 custom interview questions
- 🎯 Get AI-generated scores + explanations
- 💾 Save results locally as JSON files
- 🌐 Built with Streamlit — fast, responsive UI

---

## 🚀 How to Run the App Locally

### ✅ Prerequisites

Before running the app, ensure you have the following installed:

- Python 3.9+
- `pip` (Python package installer)
- A Google Gemini API key ([Get one here](https://makersuite.google.com/)) 

---

### 📦 Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/govardhan2022/quasivo-basic-AI_screening 
   cd qquasivo-basic-AI_screening

2. **Install dependencie** 
   pip install -r requirements.txt

3. **Set up your Gemini API key**
to .env, add your API key:
🔐 Add .env to your .gitignore to prevent exposing your API key.
  GEMINI_API_KEY="your_api_key_here"

4. **Run the app**
  streamlit run app.py

🗂️ Folder Structure
    quasivo-ai-screening/
    │
    ├── app.py                     # Main application code
    ├── requirements.txt           # List of required Python packages
    ├── .env.example               # Template for environment variables
    ├── .gitignore                 # Files to ignore in Git
    ├── README.md                  # This file
    ├── LICENSE                    # MIT License
    │
    ├── prompts/                   # Prompt templates for Gemini
    │   ├── generate_questions_prompt.txt
    │   └── score_answer_prompt.txt
    │
    └── data/                      # Saved screening results (JSON format)
        └── screening_YYYYMMDD_HHMMSS.json