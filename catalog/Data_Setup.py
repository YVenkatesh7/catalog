import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class BykeCompanyName(Base):
    __tablename__ = 'bykecompanyname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="bykecompanyname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class BykeName(Base):
    __tablename__ = 'bykename'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    year = Column(String(150))
    color = Column(String(150))
    cc = Column(String(150))
    price = Column(String(10))
    byketype = Column(String(250))
    date = Column(DateTime, nullable=False)
    bykecompanynameid = Column(Integer, ForeignKey('bykecompanyname.id'))
    bykecompanyname = relationship(
        BykeCompanyName, backref=backref('bykename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="bykename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'year': self. year,
            'color': self. color,
            'cc': self. cc,
            'price': self. price,
            'byketype': self. byketype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///bykes.db')
Base.metadata.create_all(engin)
