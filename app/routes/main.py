from flask import Blueprint, jsonify, flash, redirect, url_for, request, render_template
import stripe
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re
from app.models.user import User
from app import db
from app.models.person import Person
from app.models.newsletter import Newsletter
from app.models.project import Project
from app.models.event import Event
from app.models.faq import Faq

load_dotenv()
stripe.api_key = os.getenv("STRIPE_KEY")

main = Blueprint('main', __name__)



# helper to verify recaptcha
def verify_recaptcha(response_token, remote_ip=None, timeout=5):
    """
    Send response_token to Google and return (ok: bool, payload: dict).
    """
    secret = os.getenv("CAPTCHA_SERVER_KEY")
    if not secret:
        # Missing server key – treat as failure but log/notify appropriately
        return False, {"error": "missing-server-key"}

    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    try:
        r = requests.post(
            verify_url,
            data={
                "secret": secret,
                "response": response_token,
                "remoteip": remote_ip,
            },
            timeout=timeout,
        )
        r.raise_for_status()
        payload = r.json()
        return bool(payload.get("success")), payload
    except requests.RequestException as exc:
        # network/timeout/etc
        return False, {"error": "network-error", "exception": str(exc)}

# map some typical error codes to user-friendly messages
RECAPTCHA_ERROR_MESSAGES = {
    "missing-input-secret": "The captcha secret key is missing on the server.",
    "invalid-input-secret": "The captcha secret key is invalid.",
    "missing-input-response": "Please complete the captcha challenge.",
    "invalid-input-response": "The captcha response is invalid or malformed.",
    "bad-request": "Invalid captcha verification request.",
    "timeout-or-duplicate": "Captcha request timed out or was already used; please try again.",
    "network-error": "Unable to validate captcha due to network error. Please try again later.",
    "missing-server-key": "Captcha not configured on the server. Contact admin.",
}

@main.route('/')
def home():
    projects = Project.query.all()

    return render_template('index.html', projects=projects, captcha_site_key=os.getenv("CAPTCHA_SITE_KEY"))

@main.route('/about')
def about():

    return render_template('about.html',)

@main.route('/events')
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)


@main.route('/projects')
def projects():
    projects = Project.query.all()

    project_data = []
    for project in projects:
        soup = BeautifulSoup(project.content or "", 'html.parser')
        images = [
            img['src'].lstrip('/') for img in soup.find_all('img') if img.has_attr('src')
        ]
        project_data.append({
            'project': project,
            'images': images
        })

    return render_template('projects.html', project_data=project_data)

@main.route('/newsletters')
def newsletters():
    newsletters = Newsletter.query.all()
    return render_template('newsletters.html', newsletters=newsletters)

@main.route('/faq')
def faq():
    users = User.query.all()
    return render_template('about.html')

@main.route('/what_is_clt')
def what_is_clt():
    return render_template('what_clt.html')

@main.route('/bradwell_clt')
def bradwell_clt():
    return render_template('projects.html')

@main.route('/board_of_directors')
def board():
    people = Person.query.all()    

    return render_template('board.html', people=people)

@main.route('/view_project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_view.html', project=project)

@main.route('/signup')
def signup():
    return render_template('member_form.html')  

import os
import re
import requests
from dotenv import load_dotenv
from flask import flash, redirect, request, url_for
from sqlalchemy.exc import SQLAlchemyError

# load .env (call once at module import)
load_dotenv()

# helper to verify recaptcha
def verify_recaptcha(response_token, remote_ip=None, timeout=5):
    """
    Send response_token to Google and return (ok: bool, payload: dict).
    """
    secret = os.getenv("CAPTCHA_SERVER_KEY")
    if not secret:
        # Missing server key – treat as failure but log/notify appropriately
        return False, {"error": "missing-server-key"}

    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    try:
        r = requests.post(
            verify_url,
            data={
                "secret": secret,
                "response": response_token,
                "remoteip": remote_ip,
            },
            timeout=timeout,
        )
        r.raise_for_status()
        payload = r.json()
        return bool(payload.get("success")), payload
    except requests.RequestException as exc:
        # network/timeout/etc
        return False, {"error": "network-error", "exception": str(exc)}

# map some typical error codes to user-friendly messages
RECAPTCHA_ERROR_MESSAGES = {
    "missing-input-secret": "The captcha secret key is missing on the server.",
    "invalid-input-secret": "The captcha secret key is invalid.",
    "missing-input-response": "Please complete the captcha challenge.",
    "invalid-input-response": "The captcha response is invalid or malformed.",
    "bad-request": "Invalid captcha verification request.",
    "timeout-or-duplicate": "Captcha request timed out or was already used; please try again.",
    "network-error": "Unable to validate captcha due to network error. Please try again later.",
    "missing-server-key": "Captcha not configured on the server. Contact admin.",
}

# Example route (integrate into your existing route)
@main.route('/faq_form', methods=['POST'])
def faq_form():
    e_add = (request.form.get('email') or "").strip()
    question = (request.form.get('question') or "").strip()
    recaptcha_token = request.form.get('g-recaptcha-response')

    # Validate email
    if not e_add or not re.match(r"[^@]+@[^@]+\.[^@]+", e_add):
        flash("Please enter a valid email address.", "error")
        return redirect(request.referrer or url_for('main.index'))

    # Validate question
    if not question or len(question) < 5:
        flash("Please enter a valid question (at least 5 characters).", "error")
        return redirect(request.referrer or url_for('main.index'))

    # Ensure recaptcha token exists
    if not recaptcha_token:
        flash("Please complete the captcha.", "error")
        return redirect(request.referrer or url_for('main.index'))

    # Verify reCAPTCHA with Google
    ok, payload = verify_recaptcha(recaptcha_token, remote_ip=request.remote_addr)
    if not ok:
        # build a friendly message from possible error codes
        error_codes = payload.get("error-codes") or []
        # If verify_recaptcha returned a custom error (network etc), handle that too
        if "error" in payload and payload["error"] in RECAPTCHA_ERROR_MESSAGES:
            friendly = RECAPTCHA_ERROR_MESSAGES[payload["error"]]
        elif error_codes:
            friendly = "; ".join(RECAPTCHA_ERROR_MESSAGES.get(c, c) for c in error_codes)
        else:
            friendly = "Captcha verification failed. Please try again."

        flash(friendly, "error")
        return redirect(request.referrer or url_for('main.index'))

    # Optional: enforce max lengths
    if len(e_add) > 255 or len(question) > 2000:
        flash("Input too long.", "error")
        return redirect(request.referrer or url_for('main.index'))

    # Save submission
    faq = Faq(email=e_add, question=question, displayed=False, answered=False)
    try:
        db.session.add(faq)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("There was an error saving your question. Please try again.", "error")
        return redirect(request.referrer or url_for('main.index'))

    flash("Thanks — your question was submitted.", "success")
    return redirect(request.referrer or url_for('main.index'))


@main.route('/donations')
def donations():
    return render_template('donations.html')


@main.route('/create-checkout-session', methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json()
        amount = data.get("amount")
        if not amount or amount < 100:  # 100 pence = £1 minimum
            return jsonify(error="Invalid donation amount."), 400

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": "Donation",
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:5000/",
            cancel_url="http://localhost:5000/donations",
        )
        return jsonify({"url": session.url})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(error=str(e)), 400