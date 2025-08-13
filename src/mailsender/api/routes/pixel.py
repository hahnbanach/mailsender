from datetime import datetime

from fastapi import APIRouter, Response
from sqlalchemy.orm import Session

from ...db.models import Lead
from ...db.session import SessionLocal
from ...services import mrcall_client

router = APIRouter()

# 1x1 transparent GIF
PIXEL_GIF = (
    b"GIF89a"  # header
    b"\x01\x00\x01\x00\x80\x01\x00"
    b"\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@router.get("/p/{pixel_id}")
def pixel(pixel_id: str) -> Response:
    db: Session = SessionLocal()
    lead = db.query(Lead).filter(Lead.pixel_url == pixel_id).first()
    if lead and not lead.opened_at:
        lead.opened_at = datetime.utcnow()
        db.add(lead)
        db.commit()
        contact = mrcall_client.create_contact(lead.phone_number or "", lead.email_address)
        mrcall_client.start_call(contact.get("id", ""))
    db.close()
    return Response(content=PIXEL_GIF, media_type="image/gif")
