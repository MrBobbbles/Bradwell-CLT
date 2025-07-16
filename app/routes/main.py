from flask import Blueprint, jsonify, request, render_template
from bs4 import BeautifulSoup
from app.models.user import User
from app import db
from app.models.person import Person
from app.models.newsletter import Newsletter
from app.models.paragraph import Paragraph
from app.models.project import Project


main = Blueprint('main', __name__)


@main.route('/')
def home():
    # Query users from the database
    return render_template('index.html')

@main.route('/about')
def about():
    # Query users from the database
    users = User.query.all()
    return render_template('about.html', users=users)

@main.route('/events')
def events():
    pro = User.query.all()
    return render_template('events.html', users=pro)

@main.route('/projects')
def projects():
    projects = Project.query.all()

    project_data = []
    for project in projects:
        soup = BeautifulSoup(project.about or "", 'html.parser')
        # Extract all <img src="..."> values
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



@main.route('/add_test_person')
def add_test_person():
    try:
        # Create a test person
        test_person = Person(name="Test User", employment="Works at home", image_url="static/images/bradwell.jpg")
        db.session.add(test_person)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Test person added successfully!",
            "person": {"id": test_person.id, "name": test_person.name, "employment": test_person.employment}
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
    
