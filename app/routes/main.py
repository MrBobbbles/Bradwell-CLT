from flask import Blueprint, jsonify, flash, redirect, url_for, request, render_template
from bs4 import BeautifulSoup
import re
from app.models.user import User
from app import db
from app.models.person import Person
from app.models.newsletter import Newsletter
from app.models.project import Project
from app.models.event import Event
from app.models.email import Email


main = Blueprint('main', __name__)


@main.route('/')
def home():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

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

@main.route('/email_form', methods=['POST'])
def email_form():
    e_add = request.form.get('email')

    # Basic regex email validation
    if not e_add or not re.match(r"[^@]+@[^@]+\.[^@]+", e_add):
        flash("Please enter a valid email address.", "error")
        return redirect(request.referrer or url_for('main.index'))

    # Save email
    email = Email(email=e_add)
    db.session.add(email)
    db.session.commit()

    flash("Thanks for subscribing!", "success")
    return redirect(request.referrer or url_for('main.index'))
