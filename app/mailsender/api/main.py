import asyncio
import logging
import time
from json import JSONDecodeError
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from ..db.models import Campaign, Contact
from ..db.session import SessionLocal
from ..services.mrcall_client import start_call
from ..config.settings import settings

logger = logging.getLogger(__name__)
app = FastAPI()


SENSITIVE_HEADERS = {"authorization", "cookie"}


def _redact_headers(headers):
    return {
        key: ("***redacted***" if key.lower() in SENSITIVE_HEADERS else value)
        for key, value in headers.items()
    }


def _format_body_preview(body: bytes, limit: int = 2048) -> str:
    if not body:
        return ""
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        text = body.decode("utf-8", errors="replace")
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<truncated {len(text) - limit} chars>"


def _log_call_details(
    request: Request,
    response,
    request_body: bytes,
    duration_ms: float,
    error: Exception | None,
):
    client = request.client
    client_repr = f"{client.host}:{client.port}" if client else "unknown"
    query = request.url.query
    full_path = request.url.path + (f"?{query}" if query else "")
    request_headers = _redact_headers(request.headers)
    response_headers = _redact_headers(response.headers) if response else {}
    request_body_preview = _format_body_preview(request_body)
    status_code = response.status_code if response else 500
    error_suffix = f" error={error!r}" if error else ""

    logger.debug(
        "HTTP %s %s from %s headers=%s body=%s -> %d in %.2fms response_headers=%s%s",
        request.method,
        full_path,
        client_repr,
        request_headers,
        request_body_preview,
        status_code,
        duration_ms,
        response_headers,
        error_suffix,
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_body = await request.body()
    start = time.perf_counter()
    response = None
    error = None
    try:
        response = await call_next(request)
        return response
    except Exception as exc:  # pragma: no cover - defensive logging
        error = exc
        raise
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        _log_call_details(request, response, request_body, duration_ms, error)


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


async def _delayed_start_call(phone_number: str) -> None:
    await asyncio.sleep(settings.send_email_delay_sec)
    await asyncio.to_thread(start_call, phone_number)


def _commit_with_retry(db: Session, retries: int = 3) -> None:
    for attempt in range(retries):
        try:
            db.commit()
            return
        except OperationalError:
            db.rollback()
            if attempt == retries - 1:
                raise
            time.sleep(0.1)


@app.get("/sms_tracking")
async def sms_tracking(
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
                ).first()
            )
        except JSONDecodeError as exc:
            logger.error("Malformed contact data for msisdn %s: %s", msisdn, exc)
            raise HTTPException(status_code=400, detail="Malformed contact data")
        if contact:
            variables = contact.variables or {}
            variables["sms_delivered"] = "true"
            phone_number = variables.get("phone_number")
            if variables.get("phonecall_made") != "true" and phone_number:
                variables["phonecall_made"] = "true"
                contact.variables = variables
                _commit_with_retry(db)
                logger.info(
                    "Updated contact %s sms_delivered=true, phonecall_made=true",
                    contact.id,
                )
                asyncio.create_task(_delayed_start_call(phone_number))
            else:
                contact.variables = variables
                _commit_with_retry(db)
                logger.info(
                    "Updated contact %s sms_delivered=true, phonecall_made=%s",
                    contact.id,
                    variables.get("phonecall_made"),
                )
    return {"status": "ok"}
