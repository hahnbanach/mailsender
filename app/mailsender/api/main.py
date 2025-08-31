import logging
from json import JSONDecodeError
from fastapi import Depends, FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Dict, Optional, List

from ..db.models import Campaign, Contact
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
            contact = (
                db.query(Contact)
                .filter(Contact.emails[0]["address"].as_string() == event.email)
                .first()
            )
            if contact:
                variables = contact.variables or {}
                phone_number = variables.get("phone_number")
                phonecall_made = variables.get("phonecall_made") == "true"
                if not phonecall_made and phone_number:
                    start_call(phone_number)
                    variables["phonecall_made"] = "true"
                    contact.variables = variables
                    db.commit()
                    logger.info(
                        "Updated contact %s phonecall_made=true", contact.id
                    )
        elif event.event == "unsubscribe":
            contact = (
                db.query(Contact)
                .filter(Contact.emails[0]["address"].as_string() == event.email)
                .first()
            )
            if contact:
                variables = contact.variables or {}
                variables["opt_in"] = "false"
                contact.variables = variables
                db.commit()
                logger.info("Updated contact %s opt_in=false", contact.id)
    db.commit()
    return {"status": "ok"}


@app.get("/sms_tracking")
def sms_tracking(
    request: Request,
    status: str,
    msisdn: str,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    logger.debug("Vonage DLR: %s", dict(request.query_params))
    if status == "delivered":
        try:
            contact = (
                db.query(Contact)
                .filter(
                    or_(
                        Contact.variables["phone_number"].as_string() == msisdn,
                        Contact.variables["phone_number"].as_string() == f"+{msisdn}",
                    )
                )
                .first()
            )
        except JSONDecodeError as exc:
            logger.error("Malformed contact data for msisdn %s: %s", msisdn, exc)
            raise HTTPException(status_code=400, detail="Malformed contact data")
        if contact:
            variables = contact.variables or {}
            variables["sms_delivered"] = "true"
            if variables.get("phonecall_made") != "true":
                phone_number = variables.get("phone_number")
                if phone_number:
                    start_call(phone_number)
                    variables["phonecall_made"] = "true"
            contact.variables = variables
            db.commit()
            logger.info(
                "Updated contact %s sms_delivered=true, phonecall_made=%s",
                contact.id,
                variables.get("phonecall_made"),
            )
    return {"status": "ok"}
