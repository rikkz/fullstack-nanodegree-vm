from flask import Flask , render_template , request ,redirect , url_for , jsonify , flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Tutor, Student , User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Tutor list Application"


engine = create_engine('sqlite:///tutorstudent.db')
Base.metadata.bind = engine
DBSession = sessionmaker( bind = engine )
session = DBSession()

app = Flask(__name__)

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID( login_session['email'] )
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print login_session

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect', methods=['GET', 'POST'])
def gdisconnect():

    # Only disconnect a connected user.

    credentials = login_session.get('credentials')
    if credentials is None:
        flash('Current user not connected')
        return redirect(url_for('showTutors'))

    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    if result['status'] != '200':
        response = \
            make_response(json.dumps('''Failed to revoke token for given user!\
                result = %s credentials = %s ''' % (result, credentials)), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE  = state , log = login_session)


@app.route('/')
@app.route('/tutors')
def showTutors():
    quer = session.query(Tutor).all()
    # print login_session['email']
    return render_template('tutors.html' , items = quer , log = login_session)

@app.route('/tutors/JSON')
def tutorsJSON():
    r = session.query(Tutor).all()
    return jsonify(Items = [ i.serialize for i in r ])

@app.route('/tutor/<int:tutor_id>/student/JSON')
def StudentJSON( tutor_id ):
    items = session.query(Student).filter_by(tutor_id = tutor_id).all()
    return jsonify(Items = [ i.serialize for i in items ])

@app.route('/tutor/<int:tutor_id>/student/<int:student_id>/JSON')
def specificStudentJSON( tutor_id , student_id):
    items = session.query(Student).filter_by(tutor_id = tutor_id , id = student_id).all()
    return jsonify(Items = [ i.serialize for i in items ])

@app.route('/student/JSON')
def StudentsJSON():
    items = session.query(Student).all()
    return jsonify(Items = [ i.serialize for i in items ])


@app.route('/tutor/new' , methods = ['GET' , 'POST'])
def newTutor():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        newT = Tutor( name = name , course_teaching = course , user_id = login_session['user_id'] )
        session.add( newT )
        session.commit()
        flash("New Tutor Created")
        return redirect(url_for('showTutors'))
    else:
        return render_template('newTutor.html' , log = login_session)

@app.route('/tutor/<int:tutor_id>/edit' ,  methods = ['GET' , 'POST'])
def editTutor(tutor_id):
    if 'username' not in login_session:
        return redirect('/login')

    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    if login_session['user_id'] != quer.user_id:
        flash('You cant Edit This Profile ')
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id ))

    if request.method == 'POST':
        if request.form['name'] :
            quer.name = request.form['name']
        if request.form['course'] :
            quer.course_teaching = request.form['course']
        session.add( quer )
        session.commit()
        flash('Profile is Edited ')
        return redirect(url_for('showTutors'))
    elif request.method == 'GET':
        return render_template('editTutor.html' , i = quer , log = login_session)

@app.route('/tutor/<int:tutor_id>/delete' ,  methods = ['GET' , 'POST'])
def deleteTutor(tutor_id):
    if 'username' not in login_session:
        return redirect('/login')
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()

    if login_session['user_id'] != quer.user_id:
        flash('You cant Delete This Profile ')
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id ))

    quer2 = session.query(Student).filter_by( tutor_id = tutor_id ).all()
    if request.method == 'POST':
        for i in quer2:
            session.add( i )
            session.delete( i )
            session.commit()
        session.add(quer)
        name = quer.name
        session.delete(quer)
        session.commit()
        flash('You have just deleted the %s profile' % name)
        return redirect( url_for('showTutors'))
    else:
        return render_template('deleteTutor.html' , i = quer , log = login_session)


@app.route('/tutor/<int:tutor_id>')
@app.route('/tutor/<int:tutor_id>/student')
def showTutorStudent(tutor_id, methods = ['GET' , 'POST']):
    if 'username' not in login_session:
        return redirect('/login')

    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    if request.method == 'POST':
        return 'This page brings list of students of particular tutor'
    else:
        nq = session.query(Student).filter_by( tutor_id = tutor_id ).all()
        return render_template('student.html' , inf = quer , item = nq ,log = login_session)


@app.route('/tutor/<int:tutor_id>/student/new' , methods = ['GET' , 'POST'])
def newTutorStudent( tutor_id ):
    if 'username' not in login_session:
        return redirect('/login')

    quer2 = session.query(Tutor).filter_by( id = tutor_id ).one()
    if login_session['user_id'] != quer2.user_id:
        flash('Cant Add New Student To others Tutor ')
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id ))

    if request.method == 'POST':
        quer = Student( name = request.form['name'] , gender = request.form['gender'] , tutor_id = tutor_id , user_id = login_session['user_id'])
        session.add(quer)
        session.commit()
        flash('New Student Added')
        return redirect( url_for('showTutorStudent' , tutor_id = tutor_id ))
    else:
        return render_template('newStudent.html' , i = tutor_id , log = login_session)

@app.route('/tutor/<int:tutor_id>/student/<int:student_id>/edit', methods = ['GET' , 'POST'])
def editTutorStudent( tutor_id  , student_id):
    if 'username' not in login_session:
        return redirect('/login')

    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    nq = session.query(Student).filter_by( id = student_id ).one()

    if login_session['user_id'] != quer.user_id:
        flash('Cannot Edit other Student Profile')
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id))

    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        if name:
            nq.name = name
        if gender:
            nq.gender = gender
        session.add( nq )
        flash("Student Profile Edited")
        session.commit()
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id))
    else:
        return render_template('editStudent.html' , tutor_id = tutor_id ,i = nq , log = login_session)

@app.route('/tutor/<int:tutor_id>/student/<int:student_id>/delete' , methods = ['GET' , 'POST'])
def deleteTutorStudent( tutor_id  , student_id):
    if 'username' not in login_session:
        return redirect('/login')

    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    nq = session.query(Student).filter_by( id = student_id ).one()

    if login_session['user_id'] != quer.user_id:
        flash('Cannot delete other Student Profile')
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id))

    if request.method == 'POST':
        session.add( nq )
        session.delete( nq )
        session.commit()
        flash("Student Profile Deleted")
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id ))
    else:
        return render_template('deleteStudent.html' , i = quer , item = nq , log = login_session )

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run( host = '0.0.0.0' , port = 5000 )