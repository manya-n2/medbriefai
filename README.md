# 🩺 MedBrief AI — Clinical Note Intelligence System

> Transform raw clinical notes into structured, actionable medical insights using an AI agent pipeline.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-medbriefai--veersa.vercel.app-blue?style=flat-square)](https://medbriefai-veersa.vercel.app/)
[![Demo Video](https://img.shields.io/badge/Demo-YouTube-red?style=flat-square&logo=youtube)](https://youtu.be/AhepfgjP66o)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?style=flat-square&logo=react)](https://vitejs.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb)](https://www.mongodb.com/atlas)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Features](#-features)
- [Architecture](#-architecture)
- [Agent Workflow](#-agent-workflow)
- [Tech Stack](#-tech-stack)
- [API Reference](#-api-reference)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [Running with Docker](#-running-with-docker)
- [Project Structure](#-project-structure)
- [Team](#-team)

---

## 🔍 Overview

MedBrief AI is an **agent-based AI system** designed to reduce the cognitive burden on healthcare professionals. It takes long, unstructured clinical notes or medical reports and converts them into concise, structured outputs — complete with risk scores, drug interaction alerts, and extracted medical entities — all stored persistently in **MongoDB Atlas**.

**🔗 Live:** [medbriefai-veersa.vercel.app](https://medbriefai-veersa.vercel.app/)  
**🎥 Demo:** [Watch on YouTube](https://youtu.be/AhepfgjP66o)

---

## ❗ The Problem

Doctors and clinical staff routinely handle dense, unstructured medical notes. This leads to:

- ⏱️ **Time-consuming manual review** of lengthy documentation
- ⚠️ **Missed warning signs** buried in paragraphs of text
- 💊 **Risky drug combinations** going undetected
- 📂 **No persistent record** of analysis results for follow-up

---

## ✅ Our Solution

MedBrief AI uses an **agentic pipeline** to process clinical notes in seconds and return structured insights. Doctors get:

- A concise summary of the note
- A risk score (0–100) with category and reasoning
- Drug interaction warnings with RxNorm-backed data
- Extracted medical entities (symptoms, medications, conditions)
- All results **saved to MongoDB Atlas** for persistent storage and retrieval

---

## ✨ Features

### 📝 Smart Summarization
Converts lengthy clinical text into clean, readable summaries — highlighting the most critical medical information and reducing information overload.

### 📊 Risk Scoring
Generates a risk score from 0–100 with category labels:

| Score Range | Category |
|-------------|----------|
| 0 – 24 | 🟢 Low |
| 25 – 49 | 🟡 Moderate |
| 50 – 74 | 🟠 High |
| 75 – 100 | 🔴 Critical |

Each score includes a plain-language explanation of contributing factors.

### 💊 Drug Interaction Detection
- Identifies potentially harmful medication combinations
- Queries the **RxNorm API** for reliable, standardized drug data
- Falls back to AI-based analysis when the API doesn't cover a case

### 📄 PDF Upload Support
- Upload scanned prescriptions or printed reports as PDFs
- Automatically extracts text and feeds it into the analysis pipeline

### 🗄️ MongoDB Atlas Persistence
- All analysis results are stored in **MongoDB Atlas**
- Enables history tracking, audit trails, and future retrieval of patient note analyses

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      React Frontend                       │
│            (Vite + Glassmorphism UI, Port 3000)           │
└─────────────────────────┬────────────────────────────────┘
                          │ HTTP
┌─────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                         │
│              Agent Controller (Port 8000)                 │
│                                                           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Planner   │→ │   Executor   │→ │Response Generator│  │
│  └────────────┘  └──────┬───────┘  └──────────────────┘  │
│                         │                                 │
│            ┌────────────▼─────────────┐                  │
│            │         Tool Layer        │                  │
│            │  • Entity Extraction      │                  │
│            │  • Summarization          │                  │
│            │  • Risk Detection         │                  │
│            │  • Drug Interaction Check │                  │
│            └────────────┬─────────────┘                  │
└─────────────────────────┼────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼──────────┐        ┌──────────▼──────────┐
│    RxNorm API      │        │   MongoDB Atlas      │
│  (Drug Data)       │        │  (Result Storage)    │
└────────────────────┘        └─────────────────────┘
```

---

## 🤖 Agent Workflow

MedBrief AI uses a structured multi-step agent pattern:

```
Input (Text / PDF)
       │
       ▼
  1. PLANNER
  Determines which tools to invoke based on input content
       │
       ▼
  2. EXECUTOR (sequential tool calls)
  ┌─────────────────────────────────┐
  │  Step 1: Entity Extraction      │
  │  Step 2: Summarization          │
  │  Step 3: Drug Interaction Check │
  │  Step 4: Risk Scoring           │
  └─────────────────────────────────┘
       │
       ▼
  3. MEMORY
  Intermediate outputs passed between steps
       │
       ▼
  4. RESPONSE GENERATOR
  Combines all results → Structured JSON
       │
       ▼
  5. MONGODB ATLAS
  Stores full result for persistence
       │
       ▼
  Final Output (displayed in UI)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React (Vite), CSS (Glassmorphism) |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **AI / Agent** | Custom agent architecture, tool-driven pipeline |
| **Drug Data** | RxNorm API (NIH) |
| **Database** | MongoDB Atlas |
| **DevOps** | Docker, Docker Compose |
| **Deployment** | Vercel (frontend), Render / Railway (backend) |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)
- Docker (optional, for containerized setup)

---

### Backend

```bash
cd backend/ai-agent
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will start at `http://localhost:8000`.  
Interactive API docs available at `http://localhost:8000/docs`.

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:3000`.

---

## 🐳 Running with Docker

The entire stack (frontend + backend) can be started with a single command:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📁 Project Structure

```
medbriefai/
├── backend/
│   └── ai-agent/
│       ├── main.py              # FastAPI app entry point
│       ├── agent/
│       │   ├── planner.py       # Decides which tools to run
│       │   ├── executor.py      # Runs tool pipeline
│       │   └── memory.py        # Intermediate state management
│       ├── tools/
│       │   ├── extractor.py     # Entity extraction
│       │   ├── summarizer.py    # Text summarization
│       │   ├── risk.py          # Risk scoring logic
│       │   └── interactions.py  # Drug interaction checks
│       ├── db/
│       │   └── mongo.py         # MongoDB Atlas connection & storage
│       └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React UI components
│   │   └── App.jsx              # Main app component
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── runtime.txt
├── .gitignore
└── README.md
```

---

## 👩‍💻 Team

| Name | Role |
|------|------|
| **Manya Nigam**
| **Muskan Khatoon**
| **Anushka Goel** 

---



