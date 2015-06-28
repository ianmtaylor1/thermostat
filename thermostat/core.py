from sqlalchemy import Column, Sequence, ForeignKey
from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy import desc
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from .config import Base

class SensorGroup(Base):
    __tablename__ = 'sensorgroup'
    
    id = Column(Integer, Sequence('sensorgroup_id_seq'), primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(100))
    
    sensors = relationship("Sensor",order_by="Sensor.id",backref="group")    
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    
    def __repr__(self):
        return "<SensorGroup('{0}','{1}')>".format(self.name,self.description)

class Sensor(Base):
    __tablename__ = 'sensor'
    
    id = Column(Integer, Sequence('sensor_id_seq'), primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(100))
    group_id = Column(Integer, ForeignKey('sensorgroup.id'))
    sensortype = Column(String(32), nullable=False)
    
    __mapper_args__ = {'polymorphic_on':sensortype}
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    
    def __repr__(self):
        return "<Sensor('{0}','{1}','{2}','{3}')>".format(
            self.name,
            self.description,
            self.sensortype,
            self.group.name)
    
    def available(self):
        """Returns a boolean value indicating whether this sensor can be read.
        """
        raise NotImplementedError()
    
    def read(self):
        """Return a Reading instance representing the current temperature
        from this sensor."""
        raise NotImplementedError()
    

class Reading(Base):
    __tablename__ = 'reading'
    
    id = Column(Integer, Sequence('reading_id_seq'), primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    
    sensor = relationship('Sensor',
                backref=backref('readings',
                    order_by='desc(Reading.time)',
                    lazy='dynamic'))
    
    def __init__(self,time,value,sensor):
        self.time = time
        self.value = value
        self.sensor = sensor
    
    def __repr__(self):
        return "<Reading({0},'{1}',{2:5.1f})>".format(
            repr(self.sensor),
            self.time.strftime('%Y-%m-%d %H:%M:%S'),
            self.value)
