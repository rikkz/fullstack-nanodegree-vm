import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String , Date , Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base  = declarative_base()

class Shelter( Base ):
    __tablename__ = 'shelter'
    name = Column(String(50), nullable = False )
    id = Column( Integer , primary_key = True )
    address = Column(String(250))
    city = Column(String(250))
    state = Column(String(250))
    zipCode = Column(String(250))
    website = Column(String(250))

class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer , primary_key = True )
    name = Column(String , nullable = False )
    dateOfBirth = Column(Date)
    gender = Column(String(6) , nullable = False )
    weight = Column(Numeric(20))
    shelter_id = Column(Integer , ForeignKey('shelter.id'))
    picture = Column(String)

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all( engine)
