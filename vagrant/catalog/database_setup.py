
# sys provides functions to manipulate python run time library
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

# will be used in configuration and class code
from sqlalchemy.ext.declarative import declarative_base

# in order to create our foreign key relationships
from sqlalchemy.orm import relationship

# will be used in our configuration code
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite://restaurantmneu.db')

Base.metadata.create_all(engine)

''' __tablename__ = 'sometable' '''

class Restaurant(Base):
    ''' __tablename__ = 'restaurant' '''
    name = Column( String(80), nullable = False)
    id = Column( Integer, primary_key = True)

class MenuItems(Base):
    ''' __tablename__ = 'menu_item' '''
