# Calmate Agentic Backend - Vapi Webhook Server

A FastAPI-based webhook server for processing Vapi AI assistant call reports with structured logging, Pydantic data validation, and **Google ADK multi-agent analysis pipeline**.

## Features

- 🚀 FastAPI webhook endpoint for Vapi integration
- 📁 Type-based log folder organization
- ✅ Pydantic data validation for end-of-call reports
- 🤖 **Multi-agent AI analysis using Google ADK** (stress detection, sentiment analysis, severity classification)
- 🧪 Comprehensive test coverage
- 📊 Demo processor for testing with real data

## Project Structure

```
calmate-backend/
├── main.py                      # FastAPI webhook server
├── requirements.txt             # Python dependencies
├── models/                      # Pydantic models
│   ├── __init__.py
│   └── processed_call.py        # ProcessedCall and TranscriptMessage models
│
├── processors/                  # Data processors
│   ├── __init__.py
│   └── call_report_processor.py # End-of-call-report processor
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── log_helpers.py           # Logging utilities
│
└── logs/                        # Log files (auto-created)
    └── vapi_webhook_{type}/     # Type-based folders
        ├── raw_*.json           # Raw webhook data
        └── processed_*.json     # Processed/validated data
```

## Installation

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Open the project directory**

```bash
cd agentic-backed
```

2. **Create and activate a virtual environment** (recommended)

```bash
# Create a venv in the project (use python3 if needed)
python3 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows PowerShell)
.\\.venv\\Scripts\\Activate.ps1
```

3. **Upgrade pip and install dependencies**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment variables** (Google API key for multi-agent analysis)

```bash
cp .env.example .env
# Edit .env and set: GOOGLE_API_KEY=your_actual_api_key_here
```

- Get an API key at: `https://makersuite.google.com/app/apikey`
- The server will start without the API key; multi-agent analysis requires it.

5. **Start the server (development)**

```bash
uvicorn main:app --reload --port 3000
```

Server will be available at `http://127.0.0.1:3000`.

Notes:

- If your environment uses `python` vs `python3`, adjust commands accordingly.
- If you prefer a different venv name, replace `.venv` with your preferred name.

## Usage

### Starting the Server

```bash
uvicorn main:app --reload --port 3000
```

The server will start at `http://127.0.0.1:3000`

**Available endpoints:**

- `POST /vapi/webhook` - Webhook endpoint for Vapi

### Webhook Processing Flow

1. **Receive webhook** → Logs "Message incoming: {type}"
2. **Save raw data** → `logs/vapi_webhook_{type}/raw_{timestamp}.json`
3. **Process if end-of-call-report** → Validates with Pydantic
4. **Save processed data** → `logs/vapi_webhook_{type}/processed_{timestamp}.json`
5. **Log completion** → "Message processed: {type}"
6. **Return acknowledgment** → `{"status": "ok"}`

### Processing End-of-Call Reports

The system automatically processes end-of-call-report messages using Pydantic models:

**Extracted fields:**

- `call_id` - Unique call identifier
- `agent_id` - AI assistant identifier
- `call_type` - Type of call (webCall, inboundPhoneCall, etc.)
- `start_timestamp` - ISO format start time
- `end_timestamp` - ISO format end time
- `duration_seconds` - Call duration
- `transcript` - Simplified transcript (role + content only)

### Running the Demo Processor

Process the latest end-of-call-report log:

```bash
python demo_processor.py
```

This will:

- Find the most recent end-of-call-report log
- Process it with Pydantic validation
- Display formatted output
- Save demo results to the type folder

## Multi-Agent Analysis Pipeline 🤖

The system uses **Google ADK (Agent Development Kit)** to analyze call transcripts with 5 specialized AI agents running in parallel.

### Architecture

```
End-of-Call Report → Call Report Processor → Parent Orchestrator
                                                      ↓
                          ┌──────────────────────────┼──────────────────────────┐
                          ↓                          ↓                          ↓
                   Stress Detector          Sentiment Analyzer          Stressor Finder
                    (Flash Model)             (Flash Model)               (Flash Model)
                          ↓                          ↓                          ↓
                   Blocker Finder            Severity Classifier
                    (Flash Model)              (Pro Model - Critical)
                          ↓                          ↓
                          └──────────────────────────┼──────────────────────────┘
                                                     ↓
                                          Aggregated Analysis Report
                                        (analyzed_<call_id>.json)
```

### AI Agents

1. **Stress Detector Agent** 🔍

   - Detects stress indicators (anxiety, frustration, overwhelm)
   - Returns: `stressed_detected: boolean`

2. **Sentiment Analyzer Agent** 😊

   - Counts positive and negative expressions
   - Returns: `{"positive": int, "negative": int}`

3. **Stressor Finder Agent** 📋

   - Identifies top stressors (workload, deadlines, relationships, etc.)
   - Returns: `"workload, deadlines, manager behavior"` (comma-separated)

4. **Blocker Finder Agent** 🚧

   - Identifies obstacles preventing progress
   - Returns: `"approvals, clarity, resources"` (comma-separated)

5. **Severity Classifier Agent** ⚠️
   - Detects crisis situations requiring urgent attention
   - Uses **Gemini Pro** for higher accuracy
   - Returns: `is_severe_case: boolean`

### Analysis Output

After processing an end-of-call-report, the system generates:

```
logs/vapi_webhook_end-of-call-report_<timestamp>_<uuid>/
├── raw_<call_id>.json          # Original webhook data
├── processed_<call_id>.json     # Pydantic validated data
└── analyzed_<call_id>.json      # 🤖 AI analysis results
```

**Example `analyzed_<call_id>.json`:**

```json
{
  "call_id": "abc123",
  "call_duration_seconds": 245.5,
  "analysis_timestamp": "2025-11-25T14:30:00.000Z",
  "analysis": {
    "stressed_detected": true,
    "sentiment_counts": {
      "positive": 2,
      "negative": 8
    },
    "top_stressors": "workload, deadlines, manager behavior",
    "common_blockers": "waiting for approvals, lack of clarity",
    "is_severe_case": false
  }
}
```

## API Documentation

### POST /vapi/webhook

Receives webhook events from Vapi.

**Request Body:**

```json
{
  "message": {
    "type": "end-of-call-report",
    "call": {
      "id": "019ab9c9-c216-744e-b009-3bc3d210f73a",
      "type": "webCall"
    },
    "assistant": {
      "id": "23e8f9a7-aace-4c28-8a8f-be525dc9fd38"
    },
    "startedAt": "2025-11-25T06:53:19.677Z",
    "endedAt": "2025-11-25T06:55:00.142Z",
    "durationSeconds": 100.465,
    "messages": [
      {
        "role": "user",
        "message": "Hello!"
      }
    ]
  }
}
```

**Response:**

```json
{
  "status": "ok"
}
```

**Supported message types:**

- `end-of-call-report` - Processed and validated
- Uses type hints (Python 3.11+)
- Pydantic v2 for data validation

### Project Conventions

- Clean folder layout with logical separation
- Automated tests for all core functionality
- Comprehensive docstrings
- Clear naming conventions

### Adding New Processors

1. Create processor in `processors/` directory
2. Create Pydantic model in `models/` if needed
3. Update `main.py` to handle new message type
4. Add tests in `tests/` directory

## Dependencies

```
fastapi - Web framework
uvicorn[standard] - ASGI server
pydantic>=2.0.0 - Data validation
pytest - Testing framework
python-dateutil - Date parsing utilities
```

## License

[Add your license here]

## Contact

[Add your contact information here]
