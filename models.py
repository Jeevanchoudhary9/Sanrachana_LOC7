from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db=SQLAlchemy(app)

class User(db.Model):
    __TableName__ = 'user'
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    uname = db.Column(db.String(20), nullable=False, unique=True)
    passhash = db.Column(db.String(1024), nullable=False)
    profileid = db.Column(db.String(1024), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    #sessionid = db.Column(db.String(20), db.ForeignKey('session.sid'), nullable=True)
     
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Profile(db.Model):
    __TableName__ = 'profile'
    profileid = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20))
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    #sessionid = db.Column(db.String(20), db.ForeignKey('session.sid'), nullable=True)


with app.app_context():
    db.create_all()

    admin=User.query.filter_by(uname='admin').first()
    if not admin:
        admin=User(uname='admin', password='admin', role='manager', profileid='1')
        admin_profile=Profile(profileid='1', firstname='admin', lastname='admin',email='admin',phone='admin',address='admin')
        db.session.add(admin)
        db.session.add(admin_profile)
        db.session.commit()