from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, Optional, List

from ..db.models import Campaign
from ..db.session import SessionLocal

app = FastAPI()


class TrackingEvent(BaseModel):
    email: str
    timestamp: int
    event: str
    sg_message_id: Optional[str] = None
    smtp_id: Optional[str] = Field(default=None, alias="smtp-id")
    custom_args: Dict[str, str] = {}


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tracking")
def tracking(events: List[TrackingEvent], db: Session = Depends(get_db)) -> Dict[str, str]:
    for event in events:
        record = Campaign(
            email=event.email,
            timestamp=event.timestamp,
            event=event.event,
            sg_message_id=event.sg_message_id,
            smtp_id=event.smtp_id,
            custom_args=event.custom_args,
        )
        db.add(record)
    db.commit()
    return {"status": "ok"}
