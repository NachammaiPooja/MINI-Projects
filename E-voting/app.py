from flask import Flask , request, redirect , session, g,render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votinglist.db'
app.secret_key = '185001096'

db = SQLAlchemy(app)

class Voter(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50))
    Password=db.Column(db.String(50))
    Voterid=db.Column(db.String(50))
    Email_id = db.Column(db.String(200))
    Contact = db.Column(db.String(30))
    dob= db.Column(db.String(30))
    address=db.Column(db.String(30))
    gender=db.Column(db.String(30))
    votingstatus=db.Column(db.Integer)

class Votelist(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    v_id = db.Column(db.Integer)
    party = db.Column(db.String(50))

class Party(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50))
    
def connect_db():
    return sqlite3.connect('votinglist.db')

@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']

@app.route('/',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form['password']
        voter = Voter.query.filter_by(Email_id=email).first()
        if email=='admin' and password=='root':
            return redirect('/admin')
        if voter and voter.Password == password:
            session['username']=voter.id
            return redirect('/voting')
    return render_template('login.html')

@app.route('/register',methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        vid= request.form['voterid']
        pass1=request.form['password']
        email= request.form['email']
        contact= request.form.get('tel')
        address= request.form['address']
        dob= request.form.get('dob')
        gender= request.form['gender']
        data = Voter(Name=name,Password=pass1,Voterid=vid,Email_id=email,Contact=contact,dob=str(dob),address=address,gender=gender)
        db.session.add(data)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')

@app.route('/voting',methods=['POST', 'GET'])
def voting():
    voter = Voter.query.filter_by(id=g.user).first()
    if(voter.votingstatus==None):
        message=''
        status=1
        d = connect_db()
        query="SELECT id,Name from party "
        cur = d.execute(query)
        list = [dict( id=row[0],party=row[1]) for row in cur.fetchall()]
        d.commit()
    else:
        print('huuuuuuuuuuuuu')
        message='You have already voted'
        status=0
        list=[]
    if request.method == 'POST':
        name = request.form['button']
        data = Votelist(v_id=g.user,party=name)
        db.session.add(data)
        db.session.commit()
        d = connect_db()
        print(g.user)
        query="UPDATE voter SET votingstatus='1' where (id='"+str(g.user)+"')"
        print(query)
        cur = d.execute(query)
        d.commit()
        d.close()
        return redirect('/voting')
    return render_template('voting.html',list=list,message=message,status=status)

@app.route('/admin',methods=['POST', 'GET'])
def admin():
    d = connect_db()
    query="SELECT id,party from votelist "
    cur = d.execute(query)
    list = [dict( id=row[0],party=row[1]) for row in cur.fetchall()]
    d.commit()
    d.close()
    return render_template('admin.html',list=list)

@app.route('/addparty',methods=['POST', 'GET'])
def addparty():
    if request.method == 'POST':
        name = request.form['party']
        data = Party(Name=name)
        db.session.add(data)
        db.session.commit() 
        return redirect('/admin')
    return render_template('addparty.html')

@app.route('/logout')
def logout():
   session.pop('username', None)
   return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
