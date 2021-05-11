from operator import add
from re import A
import re
from flask import Flask, render_template, url_for , request, redirect , session, g
from flask.helpers import send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bloodbank.db'
app.static_folder = 'static'
app.config['SECRET_KEY']= '185001096'
db = SQLAlchemy(app)

class Blood(db.Model):
    __tablename__='blood'
    id = db.Column(db.Integer,primary_key=True)
    bloodtype = db.Column(db.String(5))
    volume = db.Column(db.Integer)

class Donor(db.Model):
    __tablename__='donor'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Email = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Location = db.Column(db.String(30))
    bloodtype = db.Column(db.String(5))

class Requester(db.Model):
    __tablename__='request'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Email = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Location = db.Column(db.String(30))
    bloodtype = db.Column(db.String(5))
    volume = db.Column(db.Integer)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/requestor', methods=['POST', 'GET'])
def requestor():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        contact = request.form["contact"]
        location = request.form["location"]
        bloodtype = request.form["bloodtype"]
        unit = int(request.form["unit"])
        req=Requester(Name=name,Email=email,Contact=contact,Location=location,bloodtype=bloodtype,volume=unit)
        try:
            db.session.add(req)
            db.session.commit()
        except:
            return "error adding values to database"
        rem=Blood.query.filter_by(bloodtype=bloodtype).first()
        if rem.volume-req.volume > 0:
            rem.volume =rem.volume - req.volume
            try:
                db.session.add(req)
                db.session.commit()
            except:
                return "error adding values to database"
            return render_template('available.html')
        else:
            donors= Donor.query.filter_by(bloodtype=bloodtype).all()
            return render_template('table.html',donors=donors)
    else:
        return render_template('request.html')

@app.route('/donate', methods=['POST', 'GET'])
def donate():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        contact = request.form["contact"]
        location = request.form["location"]
        bloodtype = request.form["bloodtype"]
        donor=Donor(Name=name,Email=email,Contact=contact,Location=location,bloodtype=bloodtype)
        blood=Blood.query.filter_by(bloodtype=bloodtype).first()
        blood.volume += 5
        try:
            db.session.add(donor)
            db.session.add(blood)
            db.session.commit()
        except:
            return "error adding values to database"
        return "You have Successfully donated. Thankyou!!"
    else:
        return render_template('donor.html')

if __name__ == "__main__":
    app.run(debug=True)
