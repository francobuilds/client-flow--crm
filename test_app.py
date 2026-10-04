import os
import sqlite3
import tempfile

import pytest

import app as clientflow


@pytest.fixture
def test_client():
    """
    Create an isolated temporary database for every test.
    The real clientflow.db is never touched.
    """

    db_fd, db_path = tempfile.mkstemp()

    original_database = clientflow.DATABASE
    clientflow.DATABASE = db_path

    clientflow.app.config.update(
        TESTING=True,
    )

    clientflow.init_db()

    with clientflow.app.test_client() as client:
        yield client

    clientflow.DATABASE = original_database

    os.close(db_fd)
    os.unlink(db_path)


def get_test_db():
    connection = sqlite3.connect(clientflow.DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_test_lead(test_client):
    return test_client.post(
        "/add",
        data={
            "name": "Sarah Johnson",
            "company": "Apex Media",
            "email": "sarah@apex.example",
            "status": "Qualified",
            "priority": "High",
            "notes": "Interested in website redesign.",
        },
        follow_redirects=True,
    )


def get_lead_by_email(email):
    connection = get_test_db()

    lead = connection.execute(
        "SELECT * FROM leads WHERE email = ?",
        (email,),
    ).fetchone()

    connection.close()

    return lead


def test_dashboard_loads(test_client):
    response = test_client.get("/")

    assert response.status_code == 200
    assert b"ClientFlow" in response.data
    assert b"Pipeline Dashboard" in response.data


def test_create_lead(test_client):
    response = create_test_lead(test_client)

    assert response.status_code == 200
    assert b"Apex Media" in response.data
    assert b"sarah@apex.example" in response.data

    lead = get_lead_by_email("sarah@apex.example")

    assert lead is not None
    assert lead["name"] == "Sarah Johnson"
    assert lead["company"] == "Apex Media"
    assert lead["status"] == "Qualified"
    assert lead["priority"] == "High"


def test_edit_lead(test_client):
    create_test_lead(test_client)

    lead = get_lead_by_email("sarah@apex.example")

    response = test_client.post(
        f"/edit/{lead['id']}",
        data={
            "name": "Sarah Johnson",
            "company": "Apex Media",
            "email": "sarah@apex.example",
            "status": "Proposal",
            "priority": "Medium",
            "notes": "Proposal sent. Follow up Monday.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    updated_lead = get_lead_by_email("sarah@apex.example")

    assert updated_lead is not None
    assert updated_lead["status"] == "Proposal"
    assert updated_lead["priority"] == "Medium"
    assert updated_lead["notes"] == "Proposal sent. Follow up Monday."


def test_search_leads(test_client):
    create_test_lead(test_client)

    response = test_client.get("/?search=Apex")

    assert response.status_code == 200
    assert b"sarah@apex.example" in response.data

    response = test_client.get(
        "/?search=CompanyThatDoesNotExist"
    )

    assert response.status_code == 200
    assert b"sarah@apex.example" not in response.data
    assert b"No leads found" in response.data


def test_status_filter(test_client):
    create_test_lead(test_client)

    response = test_client.get("/?status=Qualified")

    assert response.status_code == 200
    assert b"sarah@apex.example" in response.data

    response = test_client.get("/?status=Won")

    assert response.status_code == 200
    assert b"sarah@apex.example" not in response.data
    assert b"No leads found" in response.data


def test_priority_filter(test_client):
    create_test_lead(test_client)

    response = test_client.get("/?priority=High")

    assert response.status_code == 200
    assert b"sarah@apex.example" in response.data

    response = test_client.get("/?priority=Low")

    assert response.status_code == 200
    assert b"sarah@apex.example" not in response.data
    assert b"No leads found" in response.data


def test_delete_lead(test_client):
    create_test_lead(test_client)

    lead = get_lead_by_email("sarah@apex.example")

    response = test_client.post(
        f"/delete/{lead['id']}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    deleted_lead = get_lead_by_email(
        "sarah@apex.example"
    )

    assert deleted_lead is None
    assert b"sarah@apex.example" not in response.data
    assert b"No leads found" in response.data
