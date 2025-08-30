import logging
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, Optional, List

from ..db.models import Campaign, Lead
from ..db.session import SessionLocal
from ..services.mrcall_client import start_call

logger = logging.getLogger(__name__)
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("HTTP %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.debug(
        "HTTP %s %s -> %d", request.method, request.url.path, response.status_code
    )
    return response


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


@app.post("/tracking/")
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
        if event.event == "open":
            lead = db.query(Lead).filter(Lead.email_address == event.email).first()
            if lead and not lead.open_called and lead.phone_number:
                start_call(lead.phone_number)
                lead.open_called = True
        elif event.event == "unsubscribe":
            lead = db.query(Lead).filter(Lead.email_address == event.email).first()
            if lead:
                lead.opt_in = "false"
    db.commit()
    return {"status": "ok"}
