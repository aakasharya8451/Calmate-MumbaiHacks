"""
Logging utilities for webhook processing.

This module provides centralized logging utilities for saving webhook data
with a type-based folder structure that includes a timestamp and UUID per
request, ensuring isolation of each webhook POST.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Base logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def _extract_call_id(raw_data: Dict[str, Any]) -> str:
    """Extract a call identifier from the webhook payload.

    The Vapi payload typically contains the call ID at
    ``raw_data['request']['body']['message']['call_id']``.
    If it cannot be found we fall back to a short UUID.
    """
    try:
        return str(raw_data["request"]["body"]["message"]["call_id"])
    except Exception:
        # Fallback – a short random identifier
        return uuid.uuid4().hex[:8]


def save_webhook_log(
    msg_type: str,
    raw_data: Dict[str, Any],
    processed_data: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Optional[Path]]:
    """Save webhook log files with type-based folder structure.

    Creates a folder structure:
    ``logs/vapi_webhook_<type>_<timestamp>_<uuid>/``
    and stores ``raw_<call_id>.json`` and optionally
    ``processed_<call_id>.json`` inside it.

    Args:
        msg_type: The webhook message type (e.g., "end-of-call-report").
        raw_data: The complete raw webhook data to save.
        processed_data: Optional processed/transformed data to save.

    Returns:
        Tuple of (raw_file_path, processed_file_path). ``processed_file_path``
        will be ``None`` if ``processed_data`` is not provided.
    """
    # Sanitize message type for folder name (replace special chars)
    safe_type = msg_type.replace("/", "_").replace("\\", "_")

    # Extract call identifier for file naming
    call_id = _extract_call_id(raw_data)

    # Generate timestamp and UUID for unique folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    unique_id = uuid.uuid4().hex[:8]

    # Create folder: logs/vapi_webhook_<type>_<timestamp>_<uuid>/
    type_folder = LOGS_DIR / f"vapi_webhook_{safe_type}_{timestamp}_{unique_id}"
    type_folder.mkdir(exist_ok=True, parents=True)

    # Save raw JSON using call_id
    raw_filename = f"raw_{call_id}.json"
    raw_filepath = type_folder / raw_filename
    with open(raw_filepath, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    # Save processed JSON if provided, also using call_id
    processed_filepath = None
    if processed_data is not None:
        processed_filename = f"processed_{call_id}.json"
        processed_filepath = type_folder / processed_filename
        with open(processed_filepath, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

    return raw_filepath, processed_filepath


def get_latest_log_for_type(msg_type: str) -> Tuple[Optional[Path], Optional[Path]]:
    """Find the most recent raw and processed JSON files for a message type.

    The function looks for the newest folder matching the pattern
    ``vapi_webhook_<type>_<timestamp>_<uuid>`` and returns the latest
    ``raw_*.json`` and ``processed_*.json`` inside that folder.
    """
    # Sanitize message type for folder name
    safe_type = msg_type.replace("/", "_").replace("\\", "_")

    # Glob for folders that match the new naming convention
    pattern = f"vapi_webhook_{safe_type}_*_*"
    candidate_folders = sorted(LOGS_DIR.glob(pattern), reverse=True)
    if not candidate_folders:
        return None, None

    latest_folder = candidate_folders[0]

    raw_files = sorted(latest_folder.glob("raw_*.json"), reverse=True)
    raw_path = raw_files[0] if raw_files else None

    processed_files = sorted(latest_folder.glob("processed_*.json"), reverse=True)
    processed_path = processed_files[0] if processed_files else None

    return raw_path, processed_path


def save_demo_output(
    msg_type: str,
    demo_data: Dict[str, Any],
    call_id: str,
    prefix: str = "run_demo",
) -> Path:
    """Save demo output to the appropriate type folder using the same folder naming as ``save_webhook_log``.

    Args:
        msg_type: The webhook message type.
        demo_data: The demo output data to save.
        call_id: Identifier used for naming the demo file.
        prefix: Filename prefix (default: "run_demo").

    Returns:
        Path to the saved demo file.
    """
    # Sanitize message type for folder name
    safe_type = msg_type.replace("/", "_").replace("\\", "_")

    # Find the most recent folder for this type (same logic as get_latest_log_for_type)
    pattern = f"vapi_webhook_{safe_type}_*_*"
    candidate_folders = sorted(LOGS_DIR.glob(pattern), reverse=True)
    if not candidate_folders:
        # Fallback – create a new folder if none exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        unique_id = uuid.uuid4().hex[:8]
        type_folder = LOGS_DIR / f"vapi_webhook_{safe_type}_{timestamp}_{unique_id}"
        type_folder.mkdir(exist_ok=True, parents=True)
    else:
        type_folder = candidate_folders[0]

    demo_filename = f"{prefix}_{call_id}.json"
    demo_filepath = type_folder / demo_filename
    with open(demo_filepath, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return demo_filepath


def save_analysis_report(
    msg_type: str,
    analysis_data: Dict[str, Any],
    call_id: str,
) -> Path:
    """Save multi-agent analysis report to the appropriate type folder.
    
    Creates analyzed_<call_id>.json in the same folder as raw and processed logs.
    
    Args:
        msg_type: The webhook message type.
        analysis_data: The analysis report data from agents.
        call_id: Identifier used for naming the analysis file.
    
    Returns:
        Path to the saved analysis file.
    """
    # Sanitize message type for folder name
    safe_type = msg_type.replace("/", "_").replace("\\", "_")
    
    # Find the most recent folder for this type
    pattern = f"vapi_webhook_{safe_type}_*_*"
    candidate_folders = sorted(LOGS_DIR.glob(pattern), reverse=True)
    if not candidate_folders:
        # Fallback – create a new folder if none exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        unique_id = uuid.uuid4().hex[:8]
        type_folder = LOGS_DIR / f"vapi_webhook_{safe_type}_{timestamp}_{unique_id}"
        type_folder.mkdir(exist_ok=True, parents=True)
    else:
        type_folder = candidate_folders[0]
    
    analysis_filename = f"analyzed_{call_id}.json"
    analysis_filepath = type_folder / analysis_filename
    with open(analysis_filepath, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    return analysis_filepath
