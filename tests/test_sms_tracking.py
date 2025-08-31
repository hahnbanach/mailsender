import logging
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import sessionmaker
from threading import Event
from sqlalchemy.ext.mutable import MutableDict

import sys
sys.path.append("app")
from mailsender.api.main import app, get_db
from mailsender.db.models import Base, Contact


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_sms_tracking_single_call(tmp_path):
    # Setup test database
    db_url = f"sqlite:///{tmp_path}/test.db"
    logger.debug("creating database at %s", db_url)
    engine = create_engine(db_url, connect_args={"check_same_thread": False}, future=True)
    Contact.__table__.columns["variables"].type = MutableDict.as_mutable(JSON())
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Seed contact
    with TestingSessionLocal() as db:
        logger.debug("seeding contact with phone number 12345")
        contact = Contact(
            business_id="1",
            emails=[{"address": "foo@example.com"}],
            variables={"phone_number": "12345"},
        )
        db.add(contact)
        db.commit()

    client = TestClient(app)

    def perform_request(label):
        logger.debug("sending %s request", label)
        return client.get("/sms_tracking", params={"status": "delivered", "msisdn": "12345"})

    with patch("mailsender.api.main.start_call") as mock_start_call:
        started = Event()

        def delayed_call(_):
            logger.debug("start_call invoked")
            started.set()
            time.sleep(0.2)
            return {}

        mock_start_call.side_effect = delayed_call

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(perform_request, "first")
            started.wait()
            future2 = executor.submit(perform_request, "second")
            responses = [future1.result(), future2.result()]

        assert all(r.status_code == 200 for r in responses)
        assert mock_start_call.call_count == 1

    with TestingSessionLocal() as db:
        contact = db.query(Contact).first()
        assert contact.variables["phonecall_made"] == "true"
        assert contact.variables["sms_delivered"] == "true"
