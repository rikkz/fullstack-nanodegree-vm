from flask import Flask , render_template , request ,redirect , url_for , jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Tutor, Student

engine = create_engine('sqlite:///tutorstudent.db')
Base.metadata.bind = engine
DBSession = sessionmaker( bind = engine )
session = DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/tutors')
def showTutors():
    quer = session.query(Tutor).all()
    return render_template('tutors.html' , items = quer)

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
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        newT = Tutor( name = name , course_teaching = course )
        session.add( newT )
        session.commit()
        return redirect(url_for('showTutors'))
    else:
        return render_template('newTutor.html')

@app.route('/tutor/<int:tutor_id>/edit' ,  methods = ['GET' , 'POST'])
def editTutor(tutor_id):
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    if request.method == 'POST':
        if request.form['name'] :
            quer.name = request.form['name']
        if request.form['course'] :
            quer.course_teaching = request.form['course']
        session.add( quer )
        session.commit()
        return redirect(url_for('showTutors'))
    elif request.method == 'GET':
        return render_template('editTutor.html' , i = quer)

@app.route('/tutor/<int:tutor_id>/delete' ,  methods = ['GET' , 'POST'])
def deleteTutor(tutor_id):
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    quer2 = session.query(Student).filter_by( tutor_id = tutor_id ).all()
    if request.method == 'POST':
        for i in quer2:
            session.add( i )
            session.delete( i )
            session.commit()
        session.add(quer)
        session.delete(quer)
        session.commit()
        return redirect( url_for('showTutors'))
    else:
        return render_template('deleteTutor.html' , i = quer)


@app.route('/tutor/<int:tutor_id>')
@app.route('/tutor/<int:tutor_id>/student')
def showTutorStudent(tutor_id, methods = ['GET' , 'POST']):
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    if request.method == 'POST':
        return 'This page brings list of students of particular tutor'
    else:
        nq = session.query(Student).filter_by( tutor_id = tutor_id ).all()
        return render_template('student.html' , inf = quer , item = nq )


@app.route('/tutor/<int:tutor_id>/student/new' , methods = ['GET' , 'POST'])
def newTutorStudent( tutor_id ):
    if request.method == 'POST':
        quer = Student( name = request.form['name'] , gender = request.form['gender'] , tutor_id = tutor_id )
        session.add(quer)
        session.commit()
        return redirect( url_for('showTutorStudent' , tutor_id = tutor_id ))
    else:
        return render_template('newStudent.html' , i = tutor_id )

@app.route('/tutor/<int:tutor_id>/student/<int:student_id>/edit', methods = ['GET' , 'POST'])
def editTutorStudent( tutor_id  , student_id):
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    nq = session.query(Student).filter_by( id = student_id ).one()
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        if name:
            nq.name = name
        if gender:
            nq.gender = gender
        session.add( nq )
        session.commit()
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id))
    else:
        return render_template('editStudent.html' , tutor_id = tutor_id ,i = nq)

@app.route('/tutor/<int:tutor_id>/student/<int:student_id>/delete' , methods = ['GET' , 'POST'])
def deleteTutorStudent( tutor_id  , student_id):
    quer = session.query(Tutor).filter_by( id = tutor_id ).one()
    nq = session.query(Student).filter_by( id = student_id ).one()
    if request.method == 'POST':
        session.add( nq )
        session.delete( nq )
        session.commit()
        return redirect(url_for('showTutorStudent' , tutor_id = tutor_id ))
    else:
        return render_template('deleteStudent.html' , i = quer , item = nq )

if __name__ == '__main__':
    app.debug = True
    app.run( host = '0.0.0.0' , port = 5000 )