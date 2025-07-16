from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.drop_all()
    print("⚠️  Dropped all tables.")


    db.create_all()
    print("✅ Recreated all tables.")

    if not User.query.filter_by(username='testname').first():
        user = User(
            username='testname',
            password=generate_password_hash('testpass123')
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Test user created.")
    else:
        print("ℹ️ User 'testname' already exists.")

