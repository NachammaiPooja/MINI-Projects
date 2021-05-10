from operator import add
from re import A
from flask import Flask, render_template, url_for , request, redirect , session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course.db'
app.static_folder = 'static'
app.config['SECRET_KEY']= '185001112'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Department = db.Column(db.String(30))

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Department = db.Column(db.String(30))
    courses = db.relationship('Course', backref=backref("teacher", uselist=False),lazy=True)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    last_date = db.Column(db.String(30))
    domain = db.Column(db.String(50),nullable=False)
    prerequisites = db.Column(db.String(100),nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'),nullable=False)

applied = db.Table('applied',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('appstatus',db.Integer)
)



@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        passwd = request.form['pass']
        selectstudent = Student.query.filter_by(Name=username).first()
        selectteacher = Teacher.query.filter_by(Name=username).first()
        if selectstudent and selectstudent.Password == passwd:
            session['type']=1
            session['user']=selectstudent.id
            g.user=selectstudent
            return redirect('/student')
        elif selectteacher and selectteacher.Password == passwd:
            session['type']=1
            session['user']=selectteacher.id
            g.user=selectteacher
            return redirect('/teacher')
        else:
            error = "User with Given Credentials not found"
            return render_template('login.html',error=error)
    else:
        session['type']=0
        session['user']=0
        return render_template('login.html',error=None)

@app.route('/student', methods=['POST', 'GET'])
def student():
    sel_id2=db.session.execute("SELECT course_id from 'applied' WHERE student_id= :s_id AND appstatus=1",{'s_id':session["user"]}).fetchall()
    sel_id1=db.session.execute("SELECT course_id from 'applied' WHERE student_id= :s_id AND appstatus=0",{'s_id':session["user"]}).fetchall()
    sel_id=db.session.execute("SELECT course_id from 'applied' WHERE student_id= :s_id",{'s_id':session["user"]}).fetchall()
    sel=[]
    for s in sel_id:
        sel.append(s[0])
    allcourses=Course.query.filter(Course.id.notin_(sel)).all()
    sel=[]
    for s in sel_id1:
        sel.append(s[0])
    pendcourses=Course.query.filter(Course.id.in_(sel)).all()
    sel=[]
    for s in sel_id2:
        sel.append(s[0])
    appcourses=Course.query.filter(Course.id.in_(sel)).all()
    return render_template('student.html',allcourses=allcourses,pendcourses=pendcourses,appcourses=appcourses)

@app.route('/teacher', methods=['POST', 'GET'])
def teacher():
    courses=Course.query.filter_by(teacher=Teacher.query.filter_by(id=session['user']).first()).all()
    return render_template('faculty.html',courses=courses)

@app.route('/createcourse', methods=['GET','POST'])
def createcourse():
    if request.method == "POST":
        teacher = Teacher.query.filter_by(id=session['user']).first()
        course_name = request.form['subname']
        domain = request.form['domain']
        date = request.form['date']
        prereq = request.form['req']
        course = Course(name=course_name,last_date=date,prerequisites=prereq,domain=domain,teacher=teacher)
        try:
            db.session.add(course)
            db.session.commit()
        except Exception as e:
            return("error")
        return redirect('/teacher')
    else:
        return redirect('/teacher')

@app.route('/studentsignup', methods=['POST', 'GET'])
def studentsignup():
    if request.method == 'POST':
        name = request.form['uname']
        passwd = request.form['pass']
        email = request.form['email']
        contact = request.form['phone']
        dept = request.form['dept']
        stud = Student(Name=name,Password=passwd,Email_id=email,Contact=contact,Department=dept)
        try:
            db.session.add(stud)
            db.session.commit()
        except:
            return "error adding values to database"
        error = "Signed Up Successfully"
        return render_template('login.html',error=error)
    else:
        return render_template('studentsignup.html')

@app.route('/teachersignup', methods=['POST', 'GET'])
def teachersignup():
    if request.method == 'POST':
        name = request.form['uname']
        passwd = request.form['pass']
        email = request.form['email']
        contact = request.form['phone']
        dept = request.form['dept']
        teacher = Teacher(Name=name,Password=passwd,Email_id=email,Contact=contact,Department=dept)
        try:
            db.session.add(teacher)
            db.session.commit()
        except:
            return "error adding values to database"
        error = "Signed Up Successfully"
        return render_template('login.html',error=error)

    else:
        return render_template('teachersignup.html')

@app.route('/apply/<int:id>', methods=['POST', 'GET'])
def apply(id):
    d={"jid":id,"aid":session['user']}
    db.session.execute('INSERT INTO "applied" ("course_id", "student_id", "appstatus") VALUES ( :jid , :aid ,0)',d)
    db.session.commit()
    return redirect('/student')

@app.route('/seestudents/<int:id>', methods=['POST', 'GET'])
def seestudents(id):
    sel_id=db.session.execute("SELECT student_id from 'applied' WHERE course_id= :course_id AND appstatus=0",{'course_id':id}).fetchall()
    sel=[]
    course=Course.query.filter_by(id=id).first()
    for sid in sel_id:
        sel.append(sid[0])
    pendstudents=Student.query.filter(Student.id.in_(sel)).all()
    sel_id=db.session.execute("SELECT student_id from 'applied' WHERE course_id= :course_id AND appstatus=1",{'course_id':id}).fetchall()
    sel=[]
    for sid in sel_id:
        sel.append(sid[0])
    students=Student.query.filter(Student.id.in_(sel)).all()
    return render_template('viewdetails.html',pendstudents=pendstudents,course=course,students=students)


@app.route('/approve/<int:id>/<int:stid>', methods=['POST', 'GET'])
def approve(id,stid):
    db.session.execute("UPDATE 'applied' set 'appstatus'=1 WHERE course_id= :id AND student_id= :stid",{'id':id,'stid':stid})
    db.session.commit()
    return redirect(url_for("seestudents",id=id))

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    stid=session['user']
    print(id,stid)
    db.session.execute("DELETE FROM 'applied' WHERE course_id= :id AND student_id= :stid",{'id':id,'stid':stid})
    db.session.commit()
    return redirect('/student')

@app.route('/view', methods=['POST', 'GET'])
def view():
    return render_template('view.html')


if __name__ == "__main__":
    app.run(debug=True)

