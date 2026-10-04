from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "clientflow.db"


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

    new_count = connection.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'New Lead'"
    ).fetchone()[0]

    qualified_count = connection.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'Qualified'"
    ).fetchone()[0]

    proposal_count = connection.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'Proposal'"
    ).fetchone()[0]

    won_count = connection.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'Won'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        leads=leads,
        new_count=new_count,
        qualified_count=qualified_count,
        proposal_count=proposal_count,
        won_count=won_count
    )


@app.route("/add", methods=["POST"])
def add_lead():
    name = request.form["name"]
    company = request.form["company"]
    email = request.form["email"]
    status = request.form["status"]
    priority = request.form["priority"]

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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
