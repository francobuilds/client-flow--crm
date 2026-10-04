from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "clientflow.db"

VALID_STATUSES = ["New Lead", "Qualified", "Proposal", "Won"]
VALID_PRIORITIES = ["Low", "Medium", "High"]


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    # Create the database for brand-new installations.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            status TEXT NOT NULL DEFAULT 'New Lead',
            priority TEXT NOT NULL DEFAULT 'Medium',
            notes TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Safely upgrade older ClientFlow databases.
    columns = [
        row["name"]
        for row in connection.execute("PRAGMA table_info(leads)").fetchall()
    ]

    if "notes" not in columns:
        connection.execute(
            "ALTER TABLE leads ADD COLUMN notes TEXT DEFAULT ''"
        )

    if "created_at" not in columns:
        connection.execute(
            "ALTER TABLE leads ADD COLUMN created_at TEXT"
        )

    if "updated_at" not in columns:
        connection.execute(
            "ALTER TABLE leads ADD COLUMN updated_at TEXT"
        )

    # Give existing records timestamps without deleting them.
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection.execute("""
        UPDATE leads
        SET created_at = ?
        WHERE created_at IS NULL
    """, (now,))

    connection.execute("""
        UPDATE leads
        SET updated_at = ?
        WHERE updated_at IS NULL
    """, (now,))

    connection.commit()
    connection.close()


@app.route("/")
def dashboard():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    priority_filter = request.args.get("priority", "").strip()

    connection = get_db_connection()

    query = "SELECT * FROM leads WHERE 1=1"
    parameters = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR company LIKE ?
                OR email LIKE ?
                OR notes LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if status_filter in VALID_STATUSES:
        query += " AND status = ?"
        parameters.append(status_filter)

    if priority_filter in VALID_PRIORITIES:
        query += " AND priority = ?"
        parameters.append(priority_filter)

    query += " ORDER BY id DESC"

    leads = connection.execute(
        query,
        parameters
    ).fetchall()

    total_count = connection.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]

    counts = {}

    for status in VALID_STATUSES:
        counts[status] = connection.execute(
            "SELECT COUNT(*) FROM leads WHERE status = ?",
            (status,)
        ).fetchone()[0]

    high_priority_count = connection.execute(
        "SELECT COUNT(*) FROM leads WHERE priority = 'High'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        leads=leads,
        total_count=total_count,
        new_count=counts["New Lead"],
        qualified_count=counts["Qualified"],
        proposal_count=counts["Proposal"],
        won_count=counts["Won"],
        high_priority_count=high_priority_count,
        search=search,
        status_filter=status_filter,
        priority_filter=priority_filter
    )


@app.route("/add", methods=["POST"])
def add_lead():
    name = request.form.get("name", "").strip()
    company = request.form.get("company", "").strip()
    email = request.form.get("email", "").strip()
    status = request.form.get("status", "New Lead")
    priority = request.form.get("priority", "Medium")
    notes = request.form.get("notes", "").strip()

    if not name:
        return redirect(url_for("dashboard"))

    if status not in VALID_STATUSES:
        status = "New Lead"

    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO leads (
            name,
            company,
            email,
            status,
            priority,
            notes,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            company,
            email,
            status,
            priority,
            notes,
            now,
            now
        )
    )

    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


@app.route("/edit/<int:lead_id>", methods=["GET", "POST"])
def edit_lead(lead_id):
    connection = get_db_connection()

    lead = connection.execute(
        "SELECT * FROM leads WHERE id = ?",
        (lead_id,)
    ).fetchone()

    if lead is None:
        connection.close()
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        company = request.form.get("company", "").strip()
        email = request.form.get("email", "").strip()
        status = request.form.get("status", "New Lead")
        priority = request.form.get("priority", "Medium")
        notes = request.form.get("notes", "").strip()

        if not name:
            connection.close()
            return redirect(
                url_for("edit_lead", lead_id=lead_id)
            )

        if status not in VALID_STATUSES:
            status = "New Lead"

        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        connection.execute(
            """
            UPDATE leads
            SET
                name = ?,
                company = ?,
                email = ?,
                status = ?,
                priority = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name,
                company,
                email,
                status,
                priority,
                notes,
                now,
                lead_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("dashboard"))

    connection.close()

    return render_template(
        "edit_lead.html",
        lead=lead
    )


@app.route("/delete/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM leads WHERE id = ?",
        (lead_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


# Initialize the database when the application starts.
# This supports both local execution and production WSGI servers such as Gunicorn.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
