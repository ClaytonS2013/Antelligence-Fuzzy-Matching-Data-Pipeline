import os
import json
from datetime import datetime
import pandas as pd
from supabase import create_client
from typing import Optional


def get_last_run_time(log_path: str = "dedupe_log.json") -> Optional[str]:
    """
    Retrieve the last run time from a log file, or None if not found.
    """
    if not os.path.exists(log_path):
        return None
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
            return data.get("last_run_time")
    except (json.JSONDecodeError, OSError):
        return None


def update_last_run_time(timestamp: str, log_path: str = "dedupe_log.json"):
    """
    Update the log file with the current run time.
    """
    with open(log_path, "w") as f:
        json.dump({"last_run_time": timestamp}, f)


def fetch_practice_records(
    supabase_url: str,
    supabase_key: str,
    last_run_time: Optional[str] = None,
    page_size: int = 1000,
) -> pd.DataFrame:
    """
    Fetch records from the practice_records table in Supabase.
    Only records with created_at >= last_run_time are fetched if last_run_time is provided.
    Pagination is handled via the range function.
    """
    supabase = create_client(supabase_url, supabase_key)
    query = supabase.table("practice_records").select("*")
    if last_run_time:
        query = query.gte("created_at", last_run_time)
    start = 0
    rows = []
    while True:
        response = query.range(start, start + page_size - 1).execute()
        data = response.data
        if not data:
            break
        rows.extend(data)
        if len(data) < page_size:
            break
        start += page_size
    return pd.DataFrame(rows)
