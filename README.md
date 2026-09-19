# 🎓 CareerGuide AI - Student Career Guidance Chatbot (Python Version)

**CareerGuide AI** is a lightweight, modern conversational web application built for college mini-projects. It helps students explore technology careers, understand required technical skills, discover step-by-step learning roadmaps, and compare software engineering roles.

---

## 🚀 Key Features

- **Conversational Career Assistant**: Answers student queries regarding careers, required skills, programming languages, and beginner project ideas.
- **Dual AI Provider System (Primary + Fallback)**:
  - **Primary Model**: Groq (`openai/gpt-oss-20b`)
  - **Fallback Model**: SambaNova (`Meta-Llama-3.3-70B-Instruct`)
  - Automatically attempts the primary provider first and switches seamlessly to the fallback provider if the primary provider encounters an HTTP error, rate limit, or timeout.
- **Local Career Knowledge Context**: Pre-loaded with detailed structured knowledge for 10 top software domains (Software Developer, Python, Java Backend, Web Dev, AI/ML, Cybersecurity, Cloud, UI/UX, Data Science, etc.).
- **Conversation Context Memory**: Remembers previous turns within the browser session so users can ask natural follow-up questions.
- **Modern Responsive UI**: Clean bubble chat interface with loading states, suggested question chips, and model status badges.
- **Zero API Key Leakage**: Backend acts as a secure proxy to the AI providers. API keys are safely configured via `.env` file.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Python `requests`, `python-dotenv`, `pydantic`
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+), Google Fonts
- **Data & Configuration**: JSON (`careers.json`), `.env`

---

## 📁 Project Structure

```
CareerGuide-AI/
│
├── main.py                    # FastAPI Application & REST endpoint POST /api/chat
├── ai_service.py              # OpenAI API HTTP client with Primary & Fallback model logic
├── career_service.py          # Loads and formats local careers.json knowledge base
├── careers.json               # 10 Tech Career definitions & roadmaps
│
├── static/                    # Served automatically at http://localhost:8080/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── frontend/                  # Standalone frontend copy
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .env.example               # Template for environment variables
├── .env                       # Local secrets file (Git ignored)
├── .gitignore                 # Excludes secrets, __pycache__
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## 🔑 Environment Configuration

Create a `.env` file in the project root directory (refer to `.env.example`):

```ini
# Primary AI Model Configuration (Groq)
PRIMARY_API_KEY=your_groq_api_key_here
PRIMARY_BASE_URL=https://api.groq.com/openai/v1
PRIMARY_MODEL_NAME=openai/gpt-oss-20b

# Fallback AI Model Configuration (SambaNova)
FALLBACK_API_KEY=your_sambanova_api_key_here
FALLBACK_BASE_URL=https://api.sambanova.ai/v1
FALLBACK_MODEL_NAME=Meta-Llama-3.3-70B-Instruct

# Server Port
PORT=8080
```

---

## 💻 How to Run the Project

### Prerequisites
- **Python 3.10 or higher**
- **pip package manager**

### Step 1: Install Dependencies
Open terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Start the Python Server
Run the FastAPI application using Uvicorn:
```bash
python main.py
```
*(Or run `uvicorn main:app --port 8080`)*

The server will launch on `http://localhost:8080`.

### Step 3: Open the Frontend
Once the server is running, open your web browser and navigate to:
```
http://localhost:8080
```
*(Alternatively, you can open `frontend/index.html` directly in any web browser).*

---

## 📡 REST API Documentation

### `POST /api/chat`

**Request Body:**
```json
{
  "message": "What skills do I need to become a Python developer?",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello! How can I help with your career?" }
  ]
}
```

**Response (Primary Model Success):**
```json
{
  "response": "To become a Python developer, you should learn Python syntax, OOP, FastAPI/Django, REST APIs, and databases...",
  "model": "groq/compound",
  "fallbackUsed": false
}
```

**Response (Fallback Model Triggered):**
```json
{
  "response": "To become a Python developer, you should learn Python syntax, OOP, FastAPI/Django, REST APIs, and databases...",
  "model": "Meta-Llama-3.3-70B-Instruct",
  "fallbackUsed": true
}
```

---

## 💡 Example Viva Demo Questions

1. *"Which career should I choose if I like coding?"*
2. *"What skills do I need to become a Python developer?"*
3. *"How do I become an AI/ML engineer?"*
4. *"What is the difference between a data analyst and data scientist?"*
5. *"Give me a backend developer roadmap."*

---

## 🔮 Future Improvements

- Add export feature to download learning roadmaps as PDF.
- Add bookmarking for favorite career paths.
- Add quiz-based skill self-assessment for personalized career matching.
