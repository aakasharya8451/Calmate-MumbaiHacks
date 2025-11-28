from typing import Any, Dict
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

from utils.log_helpers import save_webhook_log, save_analysis_report
from processors.call_report_processor import process_end_of_call_report
from call_analyzer import analyze_call

app = FastAPI()


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request) -> Dict[str, Any]:
    """
    Webhook that receives POSTs from Vapi.

    Vapi sends:
    {
      "message": {
        "type": "<server-message-type>",
        ...
      }
    }
    """
    try:
        body: Dict[str, Any] = await request.json()
    except Exception as exc:  # invalid JSON
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    message = body.get("message")
    if not isinstance(message, dict):
        raise HTTPException(status_code=400, detail="Missing 'message' object")

    msg_type = message.get("type")
    
    # Log incoming message
    print(f"📨 Message incoming: {msg_type}")
    
    # Build complete request dump for raw logging
    timestamp_iso = datetime.now().isoformat()
    complete_dump = {
        "timestamp": timestamp_iso,
        "endpoint": "vapi_webhook",
        "request": {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            },
            "body": body
        }
    }
    
    # Process based on message type
    processed_data = None
    
    if msg_type == "end-of-call-report":
        try:
            # Process using Pydantic model
            processed_call = process_end_of_call_report(message)
            processed_data = processed_call.model_dump()
            print(f"✅ Processed end-of-call-report: call_id={processed_call.call_id}")
        except Exception as e:
            print(f"⚠️  Failed to process end-of-call-report: {e}")
            # Continue to save raw data even if processing fails
    
    # Save logs with type-based folder structure
    raw_path, processed_path = save_webhook_log(msg_type, complete_dump, processed_data)
    
    # Log saved paths
    print(f"💾 Saved to: {raw_path.parent.name}/{raw_path.name}")
    if processed_path:
        print(f"💾 Processed: {processed_path.parent.name}/{processed_path.name}")
    
    # Run multi-agent analysis for end-of-call reports
    if msg_type == "end-of-call-report" and processed_data:
        try:
            print("🤖 Starting multi-agent analysis...")
            analysis_report = await analyze_call(processed_data)
            
            # Save analysis results
            analysis_data = analysis_report.model_dump()
            analysis_path = save_analysis_report(msg_type, analysis_data, processed_data["call_id"])
            print(f"💾 Analysis: {analysis_path.parent.name}/{analysis_path.name}")
            
            # Log severity flag
            if analysis_report.analysis.is_severe_case:
                print("⚠️  🚨 SEVERE CASE DETECTED - URGENT ATTENTION REQUIRED 🚨")
            
            # Save to Database
            from database import save_call_report
            from models.analysis_models import CallReportDB
            
            print("🗄️  Saving to database...")
            # Convert to DB model
            report_db = CallReportDB.from_analysis_report(analysis_report)
            save_call_report(report_db)
            
        except Exception as e:
            print(f"⚠️  Multi-agent analysis failed: {e}")
            # Continue even if analysis fails
    
    print(f"✅ Message processed: {msg_type}")
    
    # Return acknowledgment for all events
    return {"status": "ok"}

