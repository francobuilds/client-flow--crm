# ClientFlow CRM

A lightweight sales pipeline and client relationship management application built with Flask and SQLite.

ClientFlow provides a clean workspace for managing leads from initial contact through qualification, proposal, and closed business.

## Features

- Create, view, update, and delete leads
- Persistent SQLite data storage
- Sales pipeline status tracking
- Lead priority management
- Client notes
- Search across clients, companies, email addresses, and notes
- Filter by pipeline status and priority
- Dashboard pipeline metrics
- Created and updated timestamps
- Responsive SaaS-style interface
- Automated testing with an isolated test database

## Pipeline

ClientFlow supports four opportunity stages:

- New Lead
- Qualified
- Proposal
- Won

Leads can be assigned Low, Medium, or High priority.

## Tech Stack

Backend:
- Python
- Flask
- SQLite

Frontend:
- HTML
- CSS
- Jinja templates

Testing:
- pytest
- Flask test client
- Temporary isolated SQLite databases

Production:
- Gunicorn

## Automated Testing

The automated test suite verifies:

- Dashboard availability
- Lead creation
- Lead editing
- Search
- Status filtering
- Priority filtering
- Lead deletion

Run tests with:

    python -m pytest -v

Current core test suite: 7 passing tests.

## Project Structure

    client-flow--crm/
    |-- app.py
    |-- requirements.txt
    |-- test_app.py
    |-- README.md
    |-- static/
    |   `-- style.css
    `-- templates/
        |-- dashboard.html
        `-- edit_lead.html

## Local Setup

Clone the repository:

    git clone https://github.com/francobuilds/client-flow--crm.git
    cd client-flow--crm

Install dependencies:

    python -m pip install -r requirements.txt

Run the application:

    python app.py

Then visit localhost on port 5000.

## Architecture

ClientFlow uses a server-rendered Flask architecture.

Flask handles routing and application logic, Jinja renders the interface, and SQLite provides persistent storage.

The application supports CRUD operations, search, filtering, pipeline analytics, lead notes, and database-backed state.

The automated test suite replaces the normal database path with an isolated temporary SQLite database so tests do not modify real application data.

## Development Approach

ClientFlow was developed incrementally using version-controlled checkpoints.

Core CRUD functionality was implemented first, followed by persistent storage, search and filtering, pipeline analytics, interface improvements, safe database migration, and automated testing.

Major application changes are verified against the automated test suite before being committed.

## Status

ClientFlow V1 core functionality is complete.

Next milestone: public deployment.

## Author

Franco

Technical Project Manager | Software Developer | AI Systems Builder