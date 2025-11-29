# Calmate - Agentic AI-Powered Mental Health Companion for Corporate Well-being

**Calmate** is an Agentic AI-powered Mental Health Companion that proactively connects with employees through natural, empathetic conversations on a audio phone call helping them express emotions and release work stress in a private, stigma-free way helping the corporate with anonymized, actionable well-being insights.

## 🏗️ System Architecture

The project is divided into three main components:

1.  **Frontend (`/frontend`)**:
    *   **Framework**: React 19 with Vite.
    *   **Styling**: TailwindCSS (inferred from design patterns) / CSS Modules.
    *   **Database Integration**: Supabase (Auth & Data).
    *   **Purpose**: Admin dashboard for visualizing data and managing employees.

2.  **Agentic Backend (`/agentic-backed`)**:
    *   **Framework**: FastAPI (Python).
    *   **Core Logic**: Handles webhooks from Vapi.ai, processes call logs, and orchestrates multi-agent analysis using Google Gemini and other LLMs.
    *   **Database**: PostgreSQL (via Supabase).

3.  **AI Engine (`/ai-engine`)**:
    *   **Framework**: Python Scripts.
    *   **Core Logic**: Background workers for deep data analysis, trend calculation, and report generation (PDF).
    *   **Tools**: OpenAI (GPT-4o), Matplotlib (Charts), FPDF (PDF Generation).

## 🛠️ Tech Stack

*   **Frontend**: React, TypeScript, Vite, Lucide React, Recharts (implied for charts).
*   **Backend**: Python, FastAPI, Uvicorn, Pydantic.
*   **AI & LLMs**: Google Gemini (via Google Generative AI SDK), OpenAI GPT-4o, Vapi.ai (Voice AI).
*   **Database**: PostgreSQL, Supabase.
*   **DevOps**: Docker (potential), Python venv.

## 🏁 Getting Started

### Prerequisites

*   **Node.js** (v18+)
*   **Python** (v3.10+)
*   **PostgreSQL** database (or Supabase project)
*   **Vapi.ai** Account & API Key
*   **OpenAI** API Key
*   **Google Gemini** API Key

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Calmate-MumbaiHacks.git
cd Calmate-MumbaiHacks
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

Create a `.env` file in `frontend/` with your Supabase credentials:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Run the development server:

```bash
npm run dev
```

### 3. Agentic Backend Setup

Navigate to the backend directory:

```bash
cd ../agentic-backed
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `agentic-backed/` with necessary keys:

```env
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=your_postgres_connection_string
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

### 4. AI Engine Setup

Navigate to the AI engine directory:

```bash
cd ../ai-engine
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in `ai-engine/` with necessary keys:

```env
OPENAI_API_KEY=your_openai_api_key
PG_HOST=your_db_host
PG_PORT=5432
PG_DBNAME=your_db_name
PG_USER=your_db_user
PG_PASSWORD=your_db_password
EMAIL_FROM_ADDRESS=your_email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_app_password
```

Run the worker script manually (or set up a cron job):

```bash
python worker.py
```

## 📂 Project Structure

```
Calmate-MumbaiHacks/
├── agentic-backed/       # FastAPI backend for Vapi webhooks & analysis
│   ├── agents/           # AI Agent definitions
│   ├── models/           # Pydantic models
│   ├── main.py           # Entry point
│   └── ...
├── ai-engine/            # Background workers for reporting
│   ├── worker.py         # Main reporting script
│   └── ...
├── frontend/             # React Admin Dashboard
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md             # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## 📄 License

This project is licensed under the MIT License.
