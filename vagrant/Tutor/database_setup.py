from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Tutor( Base ):
    __tablename__ = 'tutor'
    name = Column( String(250) , nullable = False )
    course_teaching = Column( String(250) , nullable = False )
    id = Column( Integer , primary_key = True )
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'Course Teaching': self.course_teaching,
            'id': self.id,
        }

class Student( Base ):
    __tablename__ = 'student'
    name = Column( String(250) , nullable = False )
    id = Column( Integer , primary_key = True )
    gender = Column( String(250) , nullable = False )
    tutor_id = Column(Integer  ,ForeignKey('tutor.id') )
    tutor = relationship(Tutor)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'gender': self.gender,
            'id': self.id,
        }


engine = create_engine('sqlite:///tutorstudent.db')
Base.metadata.create_all(engine)