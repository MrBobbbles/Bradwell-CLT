from flask import Blueprint, jsonify, request, flash, render_template, redirect, url_for, current_app
from app.models.user import User
from flask_login import login_required
from app import db
from app.models.person import Person
from app.models.project import Project
from app.models.newsletter import Newsletter
from app.models.event import Event
from app.models.info import Info
from app.models.faq import Faq
from app.models.stat import Stat

import uuid
from werkzeug.utils import secure_filename
import os



admin = Blueprint('admin', __name__)

@admin.route('/home')
@login_required
def home():
    return render_template('admin/home.html')

@admin.route('/projects')
@login_required
def projects():
    projects = Project.query.all()
    return render_template('admin/projects.html', projects=projects)


@admin.route('/delete_project/<int:project_id>')
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    print(project_id)
    try:
        db.session.delete(project)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('admin.projects'))

@admin.route('/events')
@login_required
def events():
    events = Event.query.all()
    return render_template('admin/events.html', events=events)

@admin.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        location=request.form.get('location')
        print(location)
        event = Event(name=name, description=description, date=date, location=location)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('admin.events'))
    
    return render_template('admin/add_event.html')

@admin.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        location=request.files.get('location')

        event.name = name
        event.description = description
        event.date=date
        event.location=location

        db.session.commit()
        return redirect(url_for('admin.events'))

    return render_template('admin/edit_event.html', event=event)

@admin.route('/delete_event/<int:event_id>')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    try:
        db.session.delete(event)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('admin.events'))

@admin.route('/newsletters')
@login_required
def newsletters():
    newsletters = Newsletter.query.all()
    return render_template('admin/newsletters.html', newsletters=newsletters)

@admin.route('/add_newsletter', methods=['GET', 'POST'])
@login_required
def add_newsletter():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        newsletter = request.files.get('newsletter')

        newsletter_path = None
        if newsletter and newsletter.filename:
            upload_folder = os.path.join(current_app.root_path, 'static/files/uploads')
            os.makedirs(upload_folder, exist_ok=True)  # ensure folder exists

            # Extract file extension and generate unique filename
            ext = os.path.splitext(newsletter.filename)[1]  # e.g., '.pdf'
            unique_filename = f"{uuid.uuid4().hex}{ext}"

            # Make sure filename is safe and construct full path
            safe_filename = secure_filename(unique_filename)
            full_path = os.path.join(upload_folder, safe_filename)

            # Save file
            newsletter.save(full_path)

            # Store relative path to use in templates
            newsletter_path = f'files/uploads/{safe_filename}'


        newsletter = Newsletter(name=name, description=description, date=date, filepath=newsletter_path)
        db.session.add(newsletter)
        db.session.commit()
        return redirect(url_for('admin.newsletters'))
    
    return render_template('admin/add_newsletter.html')

@admin.route('/edit_newsletter/<int:newsletter_id>', methods=['GET', 'POST'])
@login_required
def edit_newsletter(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        uploaded_file = request.files.get('newsletter') 

        # Update model fields
        newsletter.name = name
        newsletter.description = description
        newsletter.date = date

        if uploaded_file and uploaded_file.filename:
            upload_folder = os.path.join(current_app.root_path, 'static/files/uploads')
            os.makedirs(upload_folder, exist_ok=True)

            ext = os.path.splitext(uploaded_file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            safe_filename = secure_filename(unique_filename)
            full_path = os.path.join(upload_folder, safe_filename)

            uploaded_file.save(full_path)
            newsletter.file_path = f'files/uploads/{safe_filename}'

        db.session.commit()
        return redirect(url_for('admin.newsletters'))

    return render_template('admin/edit_newsletter.html', newsletter=newsletter)

@admin.route('/delete_newsletter/<int:newsletter_id>')
@login_required
def delete_newsletter(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)

    try:
        db.session.delete(newsletter)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('admin.newsletters'))

@admin.route('/people')
@login_required
def people():
    people = Person.query.all()
    return render_template('admin/people.html', people=people)

@admin.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method =='POST':
        name = request.form.get('name')
        role = request.form.get('role')
        image_file = request.files.get('image')

        filepath = None
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(current_app.root_path, 'static/images/uploads', filename)
            image_file.save(filepath)

        person = Person(name=name, role=role, image_url = f"/static/images/uploads/{filename}")
        db.session.add(person)
        db.session.flush()

        for key in request.form:
            if key.startswith('infos['):
                text = request.form[key]
                if text.strip():
                    db.session.add(Info(text=text.strip(), person_id=person.id))

        db.session.commit()
        return redirect(url_for('admin.people'))
    return render_template('admin/add_person.html')

@admin.route('/edit_person/<int:person_id>', methods=['GET', 'POST'])
@login_required
def edit_person(person_id):
    person = Person.query.get_or_404(person_id)

    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        image_file = request.files.get('image')

        person.name = name
        person.role = role

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(current_app.root_path, 'static/images/uploads', filename)
            image_file.save(filepath)
            person.image_url = f'images/uploads/{filename}'

        # Clear old infos
        Info.query.filter_by(person_id=person.id).delete()

        # Add new infos
        for key in request.form:
            if key.startswith('infos['):
                text = request.form[key]
                if text.strip():
                    db.session.add(Info(text=text.strip(), person_id=person.id))

        db.session.commit()
        return redirect(url_for('admin.people'))

    return render_template('admin/edit_person.html', person=person)

@admin.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        about = request.form.get('about')
        finished = 'finished' in request.form    
        content = request.form.get('content')
        image_file = request.files.get('cover')

        print("Files in request:", request.files)
        print("Form data:", request.form)
        filepath = None
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(current_app.root_path, 'static/images/uploads', filename)
            image_file.save(filepath)
        print(filepath)

        # Create and add the Project
        project = Project(title=title, about=about, finished=finished or False, content=content, image_url = f"/static/images/uploads/{filename}")
        db.session.add(project)
        db.session.commit()

        return redirect(url_for('admin.projects'))
    return render_template('admin/add_project.html')

@admin.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.about = request.form.get('about')
        project.finished = 'finished' in request.form
        project.content = request.form.get('content')

        image_file = request.files.get('cover')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(current_app.root_path, 'static/images/uploads', filename)
            image_file.save(filepath)
            project.image_url = f"/static/images/uploads/{filename}"

        db.session.commit()
        return redirect(url_for('admin.projects'))

    return render_template('admin/edit_project.html', project=project)

@admin.route('/delete_person/<int:person_id>')
@login_required
def delete_person(person_id):
    person = Person.query.get_or_404(person_id)

    try:
        db.session.delete(person)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('admin.people'))


@admin.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.static_folder, 'images/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    file_url = url_for('static', filename=f'images/uploads/{filename}')
    return jsonify({'location': file_url})

@admin.route('/stats')
def stats():
    stats = Stat.query.all()
    return render_template('admin/stats.html', stats=stats)

@admin.route('/stats/new', methods=['GET', 'POST'])
def new_stat():
    if request.method == 'POST':
        text = request.form.get('text')
        value = request.form.get('value')

        if not text or not value:
            flash("Please provide both text and value.", "error")
            return redirect(url_for('admin.new_stat'))

        stat = Stat(text=text, value=value)
        db.session.add(stat)
        db.session.commit()
        flash("Stat added successfully!", "success")
        return redirect(url_for('admin.stats'))

    return render_template('admin/stat_form.html', stat=None)

@admin.route('/stats/<int:stat_id>/edit', methods=['GET', 'POST'])
def edit_stat(stat_id):
    stat = Stat.query.get_or_404(stat_id)

    if request.method == 'POST':
        text = request.form.get('text')
        value = request.form.get('value')

        if not text or not value:
            flash("Please provide both text and value.", "error")
            return redirect(url_for('admin.edit_stat', stat_id=stat.id))

        stat.text = text
        stat.value = value
        db.session.commit()
        flash("Stat updated successfully!", "success")
        return redirect(url_for('admin.stats'))

    return render_template('admin/stat_form.html', stat=stat)

@admin.route('/stats/<int:stat_id>/delete', methods=['POST'])
def delete_stat(stat_id):
    stat = Stat.query.get_or_404(stat_id)
    db.session.delete(stat)
    db.session.commit()
    flash("Stat deleted successfully!", "success")
    return redirect(url_for('admin.stats_index'))


@admin.route('/faq')
def faq():
    faqs = Faq.query.all()
    return render_template('admin/faq.html', faqs=faqs)

@admin.route('/faq/<int:faq_id>', methods=['GET', 'POST'])
def faq_detail(faq_id):
    faq = Faq.query.get_or_404(faq_id)

    if request.method == 'POST':
        faq.answer = request.form.get('answer', '').strip()
        faq.answered = 'answered' in request.form
        faq.displayed = 'displayed' in request.form

        db.session.commit()
        flash("FAQ updated successfully.", "success")
        return redirect(url_for('admin.faq', faq_id=faq.id))

    return render_template('admin/faq_detail.html', faq=faq)
