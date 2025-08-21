from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime
import json
from template_loader import load_templates
from flask_cors import CORS
from api import api, init_api
from database import init_db as init_question_db

# Load form templates and define paths
FORMS_DIR = Path(__file__).parent / "forms"
TEMPLATES = load_templates()
DB_PATH = Path(__file__).parent / "database" / "forms.db"

# Initialize Flask
app = Flask(__name__)
app.secret_key = "change-me"
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.register_blueprint(api)
#init_api(api_key="REPLACE_WITH_LONG_RANDOM_VALUE")
init_api(api_key=None)
init_question_db()

# Database helpers
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS completed_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            form_json TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def get_completed_forms():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, template_name, timestamp FROM completed_forms ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows

def get_form_by_id(form_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, template_name, timestamp, form_json FROM completed_forms WHERE id = ?",
        (form_id,)
    )
    row = c.fetchone()
    conn.close()
    return row

def save_completed_form(template_name, form_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO completed_forms (template_name, timestamp, form_json) VALUES (?, ?, ?)",
        (template_name, ts, json.dumps(form_data))
    )
    conn.commit()
    conn.close()

# Routes
@app.route("/")
def index():
    init_db()
    rows = get_completed_forms()
    return render_template("index.html", rows=rows)

@app.route("/templates")
def template_list():
    return render_template("templates.html", templates=TEMPLATES)

@app.route("/fill/<template_name>", methods=["GET", "POST"])
def fill_form(template_name):
    template = TEMPLATES.get(template_name)
    if not template:
        flash("Template not found.")
        return redirect(url_for('template_list'))
    if request.method == "POST":
        data = {
            field["label"]: request.form.get(field["label"], "")
            for field in template["fields"]
            if "label" in field
        }
        save_completed_form(template_name, data)
        flash("Form submitted successfully.")
        return redirect(url_for("index"))
    return render_template(
        "fill.html",
        template_name=template_name,
        fields=template["fields"],
    )

@app.route("/view/<int:form_id>")
def view_form(form_id):
    row = get_form_by_id(form_id)
    if not row:
        flash("Form not found.")
        return redirect(url_for("index"))
    _, template_name, timestamp, form_json = row
    data = json.loads(form_json)
    return render_template(
        "view.html",
        id=form_id,
        template_name=template_name,
        timestamp=timestamp,
        data=data,
    )

@app.route("/upload", methods=["GET", "POST"])
def upload_template():
    if request.method == "POST":
        file = request.files.get("template_file")
        if file and file.filename.endswith(".json"):
            save_path = FORMS_DIR / file.filename
            file.save(save_path)
            try:
                global TEMPLATES
                TEMPLATES = load_templates()
                flash(f"Uploaded and loaded template: {file.filename}")
            except Exception as e:
                flash(f"Error loading template: {e}")
        else:
            flash("Please upload a valid JSON file.")
        return redirect(url_for("template_list"))
    return render_template("upload.html")

@app.route("/edit-template/<template_name>", methods=["GET", "POST"])
def edit_template(template_name):
    global TEMPLATES
    tmpl = TEMPLATES.get(template_name)
    if not tmpl:
        flash("Template not found.", "danger")
        return redirect(url_for("template_list"))

    # Path to the JSON file
    file_path = tmpl.get("_file", FORMS_DIR / f"{template_name}.json")
    if not Path(file_path).exists():
        flash("Template file not found.", "danger")
        return redirect(url_for("template_list"))

    if request.method == "POST":
        # Save uploaded JSON back to disk
        new_json = request.form["template_json"]
        try:
            # validate JSON
            data = json.loads(new_json)
            Path(file_path).write_text(json.dumps(data, indent=2))
            # reload into memory
            TEMPLATES = load_templates()
            flash(f"Template {template_name} updated.", "success")
            return redirect(url_for("template_list"))
        except json.JSONDecodeError as e:
            flash(f"Invalid JSON: {e}", "danger")

    # GET: show current JSON
    current = Path(file_path).read_text()
    return render_template(
        "edit_template.html",
        template_name=template_name,
        current_json=current
    )

@app.route("/edit-data/<int:form_id>", methods=["GET", "POST"])
def edit_data(form_id):
    row = get_form_by_id(form_id)
    if not row:
        flash("Form entry not found.", "danger")
        return redirect(url_for("index"))

    _, template_name, timestamp, form_json = row
    data = json.loads(form_json)

    # Use the same template definition to drive labels/types
    tmpl = TEMPLATES.get(template_name, {})
    fields = tmpl.get("fields", [])

    if request.method == "POST":
        # Rebuild updated data dict
        updated = {}
        for f in fields:
            if f.get("type") == "info" or "label" not in f:
                continue
            label = f["label"]
            if f.get("type") == "dropdown":
                updated[label] = request.form.get(label, "")
            elif f.get("type") == "number":
                updated[label] = request.form.get(label, "")
            elif f.get("type") == "textarea":
                updated[label] = request.form.get(label, "")
            else:
                updated[label] = request.form.get(label, "")
        # Persist update
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE completed_forms SET form_json = ? WHERE id = ?",
            (json.dumps(updated), form_id)
        )
        conn.commit()
        conn.close()
        flash(f"Form #{form_id} updated.", "success")
        return redirect(url_for("view_form", form_id=form_id))

    # GET: render form pre-filled
    return render_template(
        "edit_data.html",
        form_id=form_id,
        template_name=template_name,
        timestamp=timestamp,
        fields=fields,
        data=data
    )





if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)


