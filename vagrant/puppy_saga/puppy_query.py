from sqlalchemy import create_engine , func
from sqlalchemy.orm import sessionmaker

from puppy import Base , Puppy , Shelter
import datetime

engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine

DBSession = sessionmaker( bind = engine )

session = DBSession()

def query_one():
    quer = session.query(Puppy).order_by(Puppy.name.desc()).all()
    for q in quer:
        print q.name

def query_two():
    today = datetime.date.today()
    if passesLeapDay(today):
        sixMonthsAgo = today - datetime.timedelta(days = 183)
    else:
        sixMonthsAgo = today - datetime.timedelta(days = 182)


    quer = session.query(Puppy).order_by(Puppy.dateOfBirth.desc()).filter(Puppy.dateOfBirth >= sixMonthsAgo ).all()

    for qu in quer:
        print '%s : %s' % (qu.name , qu.dateOfBirth)

def query_three():
    quer = session.query(Puppy).order_by(Puppy.weight.desc()).all()
    for q in quer:
        print q.name , q.weight

def query_four():
    quer = session.query(Shelter, func.count(Puppy.id)).join(Puppy).group_by(Puppy.shelter_id).all()
    for q in quer:
        print q[ 0 ].id , q[ 0 ].name , q[1]



def passesLeapDay(today):
    """
    Returns true if most recent February 29th occured after or exactly 183 days ago (366 / 2)
    """
    thisYear = today.timetuple()[0]
    if isLeapYear(thisYear):
        sixMonthsAgo = today - datetime.timedelta(days = 183)
        leapDay = datetime.date(thisYear, 2, 29)
        return leapDay >= sixMonthsAgo
    else:
        return False

def isLeapYear(thisYear):
    """
    Returns true iff the current year is a leap year.
    Implemented according to logic at https://en.wikipedia.org/wiki/Leap_year#Algorithm
    """
    if thisYear % 4 != 0:
        return False
    elif thisYear % 100 != 0:
        return True
    elif thisYear % 400 != 0:
        return False
    else:
        return True
query_four()
