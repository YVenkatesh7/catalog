from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///bykes.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
session = DBSession()

# Delete BykesCompanyName if exisitng.
session.query(BykeCompanyName).delete()
# Delete BykeName if exisitng.
session.query(BykeName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="yekkanti venkatesh",
                 email="venkatesh.y@apssdc.in",
                 picture='sample.jpg')
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample byke companys
Company1 = BykeCompanyName(name="BAJAJ",
                     user_id=1)
session.add(Company1)
session.commit()

Company2 = BykeCompanyName(name="HERO",
                     user_id=1)
session.add(Company2)
session.commit

Company3 = BykeCompanyName(name="ROYAL ENFIELD",
                     user_id=1)
session.add(Company3)
session.commit()

Company4 = BykeCompanyName(name="TVS",
                     user_id=1)
session.add(Company4)
session.commit()

Company5 = BykeCompanyName(name="YAMAHA",
                     user_id=1)
session.add(Company5)
session.commit()

Company6 = BykeCompanyName(name="HONDA",
                     user_id=1)
session.add(Company6)
session.commit()

# Populare a bykes with models for testing
# Using different users for bykes names year also
Name1 = BykeName(name="Pulsar",
                       year="2016",
                       color="block",
                       cc="150cc",
                       price="73,650",
                       byketype="byke",
                       date=datetime.datetime.now(),
                       bykecompanynameid=1,
                       user_id=1)
session.add(Name1)
session.commit()

Name2 = BykeName(name="mastro",
                       year="2019",
                       color="blue",
                       cc="125cc",
                       price="63,000",
                       byketype="scooty",
                       date=datetime.datetime.now(),
                       bykecompanynameid=2,
                       user_id=1)
session.add(Name2)
session.commit()

Name3 = BykeName(name="thunderbird",
                       year="2018",
                       color="ash",
                       cc="350cc",
                       price="1,73,650",
                       byketype="byke",
                       date=datetime.datetime.now(),
                       bykecompanynameid=3,
                       user_id=1)
session.add(Name3)
session.commit()

Name4 = BykeName(name="jupiter",
                       year="2017",
                       color="purple",
                       cc="135cc",
                       price="55,950",
                       byketype="scooty",
                       date=datetime.datetime.now(),
                       bykecompanynameid=4,
                       user_id=1)
session.add(Name4)
session.commit()

Name5 = BykeName(name="R15",
                       year="2014",
                       color="blue",
                       cc="220cc",
                       price="1,25,650",
                       byketype="byke",
                       date=datetime.datetime.now(),
                       bykecompanynameid=5,
                       user_id=1)
session.add(Name5)
session.commit()

Name6 = BykeName(name="activa",
                       year="2019",
                       color="white",
                       cc="150cc",
                       price="73,000",
                       byketype="scooty",
                       date=datetime.datetime.now(),
                       bykecompanynameid=6,
                       user_id=1)
session.add(Name6)
session.commit()

print("Your bykes database has been inserted!")
