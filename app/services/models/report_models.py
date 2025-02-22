from pydantic import BaseModel
from typing import List
from datetime import datetime

class Report(BaseModel):
    report_id: str
    filtered_articles: List[str]
    created_at: str = datetime.now().isoformat()