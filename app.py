from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3

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

    connection.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            status TEXT NOT NULL DEFAULT 'New Lead',
            priority TEXT NOT NULL DEFAULT 'Medium'
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def dashboard():
    connection = get_db_connection()

    leads = connection.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()

    counts = {}

    for status in VALID_STATUSES:
        counts[status] = connection.execute(
            "SELECT COUNT(*) FROM leads WHERE status = ?",
            (status,)
        ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        leads=leads,
        new_count=counts["New Lead"],
        qualified_count=counts["Qualified"],
        proposal_count=counts["Proposal"],
        won_count=counts["Won"]
    )


@app.route("/add", methods=["POST"])
def add_lead():
    name = request.form.get("name", "").strip()
    company = request.form.get("company", "").strip()
    email = request.form.get("email", "").strip()
    status = request.form.get("status", "New Lead")
    priority = request.form.get("priority", "Medium")

    if not name:
        return redirect(url_for("dashboard"))

    if status not in VALID_STATUSES:
        status = "New Lead"

    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO leads (name, company, email, status, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, company, email, status, priority)
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

        if not name:
            connection.close()
            return redirect(url_for("edit_lead", lead_id=lead_id))

        if status not in VALID_STATUSES:
            status = "New Lead"

        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        connection.execute(
            """
            UPDATE leads
            SET name = ?, company = ?, email = ?, status = ?, priority = ?
            WHERE id = ?
            """,
            (name, company, email, status, priority, lead_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("dashboard"))

    connection.close()

    return render_template("edit_lead.html", lead=lead)


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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
