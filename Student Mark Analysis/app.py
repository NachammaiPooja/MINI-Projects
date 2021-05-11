from flask import Flask, url_for , request, redirect , session, g
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date,timedelta
from sqlalchemy.orm import backref
import sqlite3

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///practicals.db'
app.secret_key = '185001096'

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer,primary_key=True)
    Regno=db.Column(db.Integer)
    Name = db.Column(db.String(50))
    Year=db.Column(db.Integer)
    Dept=db.Column(db.String(50))
    Mark_1=db.Column(db.Integer)
    
    Mark_2=db.Column(db.Integer)
    
    Mark_3=db.Column(db.Integer)
    
    Mark_4=db.Column(db.Integer)
    
    Mark_5=db.Column(db.Integer)

    Result=db.Column(db.String(50))

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer,primary_key=True)
    Email = db.Column(db.String(50))
    Password = db.Column(db.String(50))
class COE(db.Model):
    __tablename__ = 'coe'
    id = db.Column(db.Integer,primary_key=True)
    Emailid = db.Column(db.String(50))
    Password = db.Column(db.String(50))

    

    
def connect_db():
    return sqlite3.connect('practicals.db')

@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']

@app.route('/',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        emailid = request.form.get('email')
        print(emailid)
        passwd = request.form.get('pass')
        print(passwd)
        selectapplicant = Student.query.filter_by(Regno=emailid,Name=passwd).first() 
        #selectapplicant1 = COE.query.filter_by(Emailid=emailid,Password=passwd).first()
        if emailid=="staff_1" and passwd=="abcde":
            return redirect('/teacherpage')
        if emailid=="coe_1" and passwd=="abcd":
            #session['username']=selectapplicant.id
            return redirect('/coepage1')
        if selectapplicant:
            
            session['username']=selectapplicant.Regno
            print(session['username'])
            print("Bye",selectapplicant.Regno)
            return redirect('/studentpage')

    return render_template('index.html')


@app.route('/studentpage',methods=['POST', 'GET'])
def studentpage():
    givenstu=Student.query.filter_by(Regno=session['username']).first()
    print(session['username'])
    print(givenstu)
    return render_template('studentpage.html',items=givenstu)
    

@app.route('/teacherpage',methods=['POST', 'GET'])
def teacherpage():
    if request.method=='POST':
        regno=request.form['numer']
        name=request.form['name']
        sem=request.form['sem']
        dept=request.form['dept']
        year=request.form['year']
        mark1=request.form['Mark1']
        mark2=request.form['Mark2']
        mark3=request.form['Mark3']
        mark4=request.form['Mark4']
        mark5=request.form['Mark5']
        if(int(mark1)>=35 and int(mark2)>=35 and int(mark3)>=35 and int(mark4)>=35 and int(mark5)>=35):
            result="pass"
        else:
            result="fail"
        data = Student(Regno=regno,Name=name,Year=year,Dept=dept,Mark_1=mark1,Mark_2=mark2,Mark_3=mark3,Mark_4=mark4,Mark_5=mark5,Result=result)
        db.session.add(data)
        db.session.commit() 
        return "Sucessfully added"
    else:
        return render_template('teacherpage.html')

    
@app.route('/coepage1',methods=['POST', 'GET'])
def coepage():
    data = Student.query.all()
    print(data)
    return render_template('coepage1.html',items=data)
@app.route('/view_stats',methods=['POST', 'GET'])
def view_pass_stats():
    passed = Student.query.filter_by(Result="pass").count()
    failed= Student.query.filter_by(Result="fail").count()
    return render_template('pass.html',items=passed,it=failed)

    


    

        


if __name__ == "__main__":
    app.run(debug=True)
