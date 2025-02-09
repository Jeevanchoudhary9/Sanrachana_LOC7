from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import base64
from sqlalchemy.ext.mutable import MutableList

db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    userid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    full_name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100), unique=True, nullable=False)
    password=db.Column(db.String(100), nullable=False)
    organization_name=db.Column(db.String(100), nullable=False)
    motto=db.Column(db.String(100), nullable=False)
    date_of_creation=db.Column(db.Date, nullable=False)
    location=db.Column(db.String(100), nullable=False)
    domain=db.Column(db.String(100), nullable=False)
    account_type=db.Column(db.String(100), nullable=False)
    logo=db.Column(db.String(1000), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def set_password(self, password):
        self.password=generate_password_hash(password)

    def serialize(self):
        return {
            'userid': self.userid,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'organization_name': self.organization_name,
            'motto': self.motto,
            'date_of_creation': self.date_of_creation,
            'location': self.location,
            'domain': self.domain,
            'account_type': self.account_type,
            'logo': self.logo
        }
    

class NGO_Project_Proposal(db.Model):
    __tablename__ = 'ngo_project_proposal'
    project_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain=db.Column(db.String(100), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.userid'), nullable=False)
    project_name=db.Column(db.String(100), nullable=False)
    budget=db.Column(db.Integer, nullable=False, default=0)
    location=db.Column(db.String(100), nullable=False)
    project_moto=db.Column(db.String(100), nullable=False)
    doners=db.Column(db.String(1000), nullable=True, default=None)
    status=db.Column(db.String(100), nullable=False)
    start_date=db.Column(db.Date, nullable=False)
    end_date=db.Column(db.Date, nullable=False)
    funds_recieved=db.Column(db.Integer, nullable=True, default=0)

    def serialize(self):
        return {
            'project_id': self.project_id,
            'domain': self.domain,
            'user_id': self.user_id,
            'project_name': self.project_name,
            'budget': self.budget,
            'location': self.location,
            'project_moto': self.project_moto,
            'doners': self.doners,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'funds_recieved': self.funds_recieved
        }
   
 
class NGO_Project_Requirement(db.Model):
    __tablename__ = 'ngo_project_requirement'
    requirement_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    project_id=db.Column(db.Integer, db.ForeignKey('ngo_project_proposal.project_id'), nullable=False)
    requirement_quantity=db.Column(db.Integer, nullable=False)
    requirment_type=db.Column(db.String(100), nullable=False)
    status=db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'requirement_id': self.requirement_id,
            'userid': self.userid,
            'project_id': self.project_id,
            'requirement_quantity': self.requirement_quantity,
            'requirment_type': self.requirment_type,
            'status': self.status,
            'project_name': NGO_Project_Proposal.query.filter_by(project_id=self.project_id).first().project_name,
            'location': NGO_Project_Proposal.query.filter_by(project_id=self.project_id).first().location,
            'logo': base64.b64encode(User.query.filter_by(userid=self.userid).first().logo).decode('utf-8')
            
        }

class Partnership(db.Model):
    __tablename__ = 'partnership'
    partnership_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngo_id=db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    corporate_id=db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    status=db.Column(db.String(100), nullable=False)
    date=db.Column(db.Date, nullable=False)
    project_id=db.Column(db.Integer, db.ForeignKey('ngo_project_proposal.project_id'), nullable=False)

    def serialize(self):
        return {
            'partnership_id': self.partnership_id,
            'ngo_id': self.ngo_id,
            'corporate_id': self.corporate_id,
            'status': self.status,
            'date': self.date,
            'corporate_name': User.query.filter_by(userid=self.corporate_id).first().organization_name,
            'project_name': NGO_Project_Proposal.query.filter_by(project_id=self.project_id).first().project_name,
            'ngo_logo': base64.b64encode(User.query.filter_by(userid=self.ngo_id).first().logo).decode('utf-8'),
            'location': NGO_Project_Proposal.query.filter_by(project_id=self.project_id).first().location,
            'ngo_location': User.query.filter_by(userid=self.ngo_id).first().location,
            'requirment_type': NGO_Project_Requirement.query.filter_by(project_id=self.project_id).first().requirment_type,
            'requirement_quantity': NGO_Project_Requirement.query.filter_by(project_id=self.project_id).first().requirement_quantity


        }
    
class Corporate_Initiative(db.Model):
    __tablename__ = 'corporate_initiative'
    initiative_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    initiative_name = db.Column(db.String(100), nullable=False)
    domain=db.Column(db.String(100), nullable=False)
    type_of_initiaitive=db.Column(db.String(100), nullable=False)
    status=db.Column(db.String(100), nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    start_date=db.Column(db.Date, nullable=False)
    end_date=db.Column(db.Date, nullable=False)
    location=db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'initiative_id': self.initiative_id,
            'user_id': self.user_id,
            'initiative_name': self.initiative_name,
            'type_of_initiaitive': self.type_of_initiaitive,
            'status': self.status,
            'quantity': self.quantity,
            'domain': self.domain,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'location': self.location,
            'logo': base64.b64encode(User.query.filter_by(userid=self.user_id).first().logo).decode('utf-8')
        }
    
class Chat(db.Model):
    __tablename__ = 'chat'
    chat_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngo_id=db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    corporate_id=db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    project_id=db.Column(db.Integer, db.ForeignKey('ngo_project_proposal.project_id'), nullable=False)
    conversation = db.Column(MutableList.as_mutable(db.JSON), default=[])
    date=db.Column(db.Date, nullable=False)


    def serialize(self):
        return {
            'chat_id': self.chat_id,
            'ngo_id': self.ngo_id,
            'corporate_id': self.corporate_id,
            'project_id': self.project_id,
            'conversation': self.conversation,
            'date': self.date,
        }
     

with app.app_context():
    db.create_all()

    admin=User.query.filter_by(username='admin').first()
    if not admin:
        admin=User(username='admin', full_name='admin',email='admin@admin.com',password='admin',organization_name='admin',motto='admin',date_of_creation=datetime.datetime.now(),location='admin',domain='admin',account_type='admin',logo='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

