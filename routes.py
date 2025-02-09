import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import distinct
from app import app
from functools import wraps
from models import db, User, NGO_Project_Proposal,Partnership,NGO_Project_Requirement,Corporate_Initiative
import random
import razorpay
from auth import auth_required, admin_required

@app.route('/')
def index():
    flash("Operation completed successfully!",'success')
    return render_template('landing.html',nav="landing")

@app.route('/ngo_dashboard')
@auth_required
def ngo_dashboard():
    NGO_Project_Proposals=NGO_Project_Proposal.query.filter_by(user_id=session['user_id']).all()
    Total_funds_recieved = 1800
    suggested=Corporate_Initiative.query.filter_by(status="Requested").all()
    suggesteds=[]
    for i in suggested:
        suggesteds.append(i.serialize())
    
    
    partnership_count = Partnership.query.filter_by(ngo_id=session['user_id']).all()
    try:
        partnership = Partnership.query.filter_by(ngo_id=session['user_id'],status="Accepted").all()
        partnerships=[]
        for i in partnership:
            partnerships.append(i.serialize())
    except:
        partnerships=[]

    return render_template('NGO_dashboard.html',nav="ngo_dashboard",NGO_Project_Proposals=NGO_Project_Proposals,projectcount=len(NGO_Project_Proposals),Total_funds_recieved=Total_funds_recieved,partnership_count=len(partnership_count),partnerships=partnerships,suggested=suggesteds)

@app.route('/collabration_management')
def collabration_management():
    return render_template('collabration_management.html',nav="collabration_management")

@app.route('/new_project_proposal', methods=["GET", "POST"])
@auth_required
def new_project_proposal():
    if request.method == "GET":
        return render_template('new_project_proposal.html',nav="new_project_proposal")
    elif request.method == "POST":
        project_name=request.form.get('project_name')
        domain=request.form.get('domain')
        project_moto=request.form.get('project_moto')
        budget=request.form.get('budget')
        start_date=datetime.datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date=datetime.datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        latitude=request.form.get('latitude')
        longitude=request.form.get('longitude')
        location=latitude+","+longitude

        user_id=session['user_id']
        # location=latitute+","+longitude
        print(project_name, domain, project_moto, budget, start_date, end_date, latitude, longitude, user_id)
        project=NGO_Project_Proposal(project_name=project_name, domain=domain, project_moto=project_moto, budget=budget, start_date=start_date, end_date=end_date, location=location, user_id=user_id, status="Acitve")
        db.session.add(project)
        db.session.commit()
        flash('Project proposal created successfully!','success')
        return redirect(url_for('ngo_dashboard'))


def get_region(lat, lng):
    lat, lng = float(lat), float(lng)

    if lat > 23 and lng < 78:
        return "North India"
    elif lat < 23 and lng > 78:
        return "South India"
    elif lat > 23 and lng > 78:
        return "East India"
    elif lat < 23 and lng < 78:
        return "West India"
    else:
        return "Central India"
    
@app.route('/corporate_dashboard')
@auth_required
def corporate_dashboard():
    partnership_count = Partnership.query.filter_by(corporate_id=session['user_id']).all()
    projects = []
    project = NGO_Project_Proposal.query.all()
    ngos_all = User.query.filter_by(account_type="NGO").all()
    allngos = User.query.filter_by(account_type="NGO").all()
    nog_all=[]
    for i in allngos:
        nog_all.append(i.serialize())
    


    

    for i in project:
        j={}
        i = i.serialize()
        lat, lng = map(float, i['location'].split(','))  # Extract lat, lng
        j['name'] = i['project_name']
        j['lat'] = lat
        j['lng'] = lng
        j['region'] = get_region(lat, lng)  # Convert lat/lng to region
        projects.append(j)
    # print(projects)

    ngos=[]
    for i in ngos_all:
        j={}
        i = i.serialize()
        lat, lng = map(float, i['location'].split(','))
        j['name'] = i['organization_name']
        j['lat'] = lat
        j['lng'] = lng
        j['region'] = get_region(lat, lng)
        ngos.append(j)


    return render_template('corporate_dashboard.html',nav="corporate_dashboard",partnership_count=len(partnership_count),projects=projects,ngos=ngos,nog_all=nog_all)

@app.route('/corporate_list')
def corporate_list():
    corp_initiative = Corporate_Initiative.query.filter_by(status="Active").all()
    corp_initiatives=[]
    for i in corp_initiative:
        corp_initiatives.append(i.serialize())
    
    projects=NGO_Project_Proposal.query.filter_by(status="Acitve").all()
    project_list=[]
    for i in projects:
        project_list.append(i.serialize())
    return render_template('corporate_list.html',nav="corporate_list",corp_initiatives=corp_initiatives,project_list=project_list)

@app.route('/ngo_list')
def ngo_list():
    ngo_requirement=NGO_Project_Requirement.query.filter_by(status="Pending").all()

    ngo_requirements=[]
    for i in ngo_requirement:
        ngo_requirements.append(i.serialize())
        

    return render_template('ngo_list.html',nav="ngo_list",ngo_requirements=ngo_requirements)

@app.route('/ngo_project_requirement' , methods=["POST"])
def ngo_project_requirement():
    data = request.json
    project_id = data['project_id']
    requirement_quantity = data['requirement_quantity']
    requirement_type = data['requirement_type']
    user_id = session['user_id']
    status = "Pending"
    requirement = NGO_Project_Requirement(project_id=project_id, requirement_quantity=requirement_quantity, requirment_type=requirement_type, userid=user_id, status=status)
    db.session.add(requirement)
    db.session.commit()
    flash('Requirement added successfully!','success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/partnership_request/<int:requirement_id>', methods=["GET"])
def partnership_request(requirement_id):
    print(requirement_id)
    userid=session['user_id']
    if User.query.filter_by(userid=userid).first().account_type=="NGO":
        ngo_id=userid
        corporate_id=NGO_Project_Requirement.query.filter_by(requirement_id=requirement_id).first().userid
        print("wait")
    elif User.query.filter_by(userid=userid).first().account_type=="Corporate":
        corporate_id=userid
        ngo_id=NGO_Project_Requirement.query.filter_by(requirement_id=requirement_id).first().userid
        Partnership_request=Partnership(ngo_id=ngo_id,corporate_id=corporate_id,status="Cor_Requested",date=datetime.datetime.now(),project_id=NGO_Project_Requirement.query.filter_by(requirement_id=requirement_id).first().project_id)
        NGO_Project_Requirement.query.filter_by(requirement_id=requirement_id).first().status="Requested"
        db.session.add(Partnership_request)
        db.session.commit()

    flash('Partnership request sent successfully!','success')
    return redirect(url_for('ngo_list'))



@app.route('/ngo_portal_accept', methods=["GET","POST"])
def ngo_portal_accept():
    if request.method == "GET":
        if User.query.filter_by(userid=session['user_id']).first().account_type=="NGO":
            partnership=Partnership.query.filter_by(ngo_id=session['user_id'],status="Cor_Requested").all()
            partnerships=[]
            for i in partnership:
                partnerships.append(i.serialize())
            return render_template('ngo_portal_accept.html',nav="ngo_portal_accept",partnerships=partnerships,ngo=True)
        elif User.query.filter_by(userid=session['user_id']).first().account_type=="Corporate":
            partnership=Partnership.query.filter_by(corporate_id=session['user_id'],status="NGO_Requested").all()
            partnerships=[]
            for i in partnership:
                partnerships.append(i.serialize())
            return render_template('ngo_portal_accept.html',nav="ngo_portal_accept",partnerships=partnerships,ngo=False)

        return render_template('ngo_portal_accept.html',nav="ngo_portal_accept")
    elif request.method == "POST":
        partnership_id=request.form.get('partnership_id')
        partnership=Partnership.query.filter_by(partnership_id=partnership_id).first()
        partnership.status="Accepted"
        db.session.commit()
        flash('Partnership request accepted successfully!','success')
        return redirect(url_for('ngo_dashboard'))
    
@app.route('/accept/<int:id>', methods=["GET"])
def accept(id):
    partnership = Partnership.query.filter_by(partnership_id=id).first()
    partnership.status="Accepted"
    NGO_Project_Requirement.query.filter_by(userid=partnership.ngo_id).first().status="Accepted"
    db.session.commit()
    print(id)
    flash('Partnership request accepted successfully!','success')
    return redirect(url_for('ngo_portal_accept'))

@app.route('/reject/<int:id>', methods=["GET"])
def reject(id):
    partnership = Partnership.query.filter_by(partnership_id=id).first()
    partnership.status="Rejected"
    NGO_Project_Requirement.query.filter_by(userid=partnership.ngo_id).first().status="Rejected"
    db.session.commit()
    print(id)
    flash('Partnership request rejected successfully!','success')
    return redirect(url_for('ngo_portal_accept'))
    

@app.route('/corporate_initiative', methods=["GET","POST"])
def corporate_initiative():
    if request.method == "GET":
        return render_template('corporate_initiative.html',nav="corporate_initiative")
    elif request.method == "POST":

        initiative_name=request.form.get('initiative_name')
        domain=request.form.get('domain')
        type_of_initiaitive=request.form.get('type_of_initiaitive')
        status="Active"
        quantity=request.form.get('quantity')
        start_date=datetime.datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date=datetime.datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        latitude=request.form.get('latitude')
        longitude=request.form.get('longitude')
        location=latitude+","+longitude
        user_id=session['user_id']

        print(initiative_name, domain, type_of_initiaitive, status, quantity, start_date, end_date, location, user_id)
        initiative=Corporate_Initiative(initiative_name=initiative_name, domain=domain, type_of_initiaitive=type_of_initiaitive, status=status, quantity=quantity, start_date=start_date, end_date=end_date, location=location, user_id=user_id)
        db.session.add(initiative)
        db.session.commit()
        flash('Corporate initiative created successfully!','success')
        return redirect(url_for('corporate_dashboard'))
    
@app.route('/partnership_request_ngo/<int:initiative_id>/<int:project_id>')
def partnership_request_ngo(initiative_id, project_id):
    
    user_id=session['user_id']
    if User.query.filter_by(userid=user_id).first().account_type=="NGO":
        ngo_id=user_id
        Corporate_Initiative.query.filter_by(initiative_id=initiative_id).first().status = "Requested"
        ngo_project_requirement = NGO_Project_Requirement(project_id=project_id, requirement_quantity=Corporate_Initiative.query.filter_by(initiative_id=initiative_id).first().quantity, requirment_type=Corporate_Initiative.query.filter_by(initiative_id=initiative_id).first().type_of_initiaitive, userid=ngo_id, status="Pending")
        partnership = Partnership(ngo_id=ngo_id, corporate_id=Corporate_Initiative.query.filter_by(initiative_id=initiative_id).first().user_id, status="NGO_Requested", date=datetime.datetime.now(), project_id=project_id)
        db.session.add(partnership)
        db.session.add(ngo_project_requirement)
        db.session.commit()

    return redirect(url_for('corporate_list'))

