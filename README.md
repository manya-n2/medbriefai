# MedBrief AI - Clinical Note Intelligence System

## Problem Statement
Users often deal with long, unstructured clinical notes or medical reports, making it difficult to quickly identify key information such as symptoms, medications, risks, and possible drug interactions.
This usually leads to:
* Time-consuming manual analysis
* Missed critical warning signs
* Risky or unsafe drug combinations

## Our Solution

MedBrief AI is an agent-based AI system that converts raw clinical notes into clear, structured, and actionable insights.
Instead of going through paragraphs of text, doctors instantly get:
* A concise summary
* A risk score (0–100)
* Drug interaction alerts
* Extracted medical entities

## Key Features

### Smart Summarization
* Transforms lengthy notes into easy-to-read summaries
* Highlights the most important medical information
* Reduces cognitive load for doctors

### Risk Prediction
* Generates a risk score between 0 and 100
* Categorizes cases into Low, Moderate, High, or Critical
* Provides simple reasoning behind the score

### Drug Interaction Detection
* Identifies harmful combinations of medications
* Uses RxNorm API for reliable medical data
* Falls back on AI-based analysis when needed

### PDF Support
* Allows users to upload prescriptions or reports
* Automatically extracts and analyzes text
* Works seamlessly with the rest of the pipeline

---

## Architecture Overview
The system follows a simple but powerful flow:
* Frontend built with React (Vite) and a clean glass-style UI
* Backend powered by FastAPI acting as the agent controller
* A tools layer that handles:
  * Entity extraction
  * Summarization
  * Risk detection
  * Drug interaction checking
* Integration with external APIs like RxNorm
* Optional MongoDB for storing memory or results


## How the Agent Works
The intelligence of MedBrief AI comes from its agent workflow:
1. Planner
   Decides which tools are needed based on input
2. Executor
   Runs tools step-by-step:
   Extract → Summarize → Interactions → Risk
3. Memory
    Stores intermediate outputs for better processing
4 Response Generator
   Combines everything into a structured JSON output

## Tech Stack
### Frontend
* React (Vite)
* CSS (Glass UI design)

### Backend
* FastAPI
* Python
* Uvicorn

### AI System
* Agent-based architecture
* Tool-driven execution pipeline

### DevOps
* Docker
* Docker Compose

### Main Endpoints
* POST /analyze
* POST /risk/score
* POST /interactions/check
* POST /summarize/text
  
## Setup Instructions
### Run Locally

Backend:
* cd backend/ai-agent
* pip install -r requirements.txt
* uvicorn main:app --reload

Frontend:
* cd frontend
* npm install
* npm run dev

##  Run with Docker
docker compose up --build
Frontend: http://localhost:3000  
Backend: http://localhost:8000/docs

## Test Cases
* Short clinical notes are summarized correctly
* Multiple medications trigger interaction detection
* High-risk symptoms increase the risk score
* PDF uploads are processed and analyzed successfully

## Demo Video

* https://youtu.be/AhepfgjP66o

## Live Deployment

* https://medbriefai-veersa.vercel.app/

## Design Approach
* Clean and minimal clinical dashboard
* Glassmorphism-based UI
* Focus on readability and usability

## Team
* Manya Nigam
* Muskan Khatoon
* Anushka Goel

## Conclusion
MedBrief AI is built to make a doctor’s workflow faster, safer, and more efficient. By turning complex clinical notes into structured insights, it helps reduce errors, save time, and support better clinical decisions.
