from sqlalchemy import Column, Sequence, ForeignKey
from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy import desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

from urllib.parse import urlencode
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import re

from w1thermsensor.core import W1ThermSensor,NoSensorFoundError

"""Base class for use in this module."""
Base = declarative_base()

class SensorGroup(Base):
    """Class defining an organizational unit of sensors."""
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
    """Base class of a sensor. Specific sensor types should subclass
    this class and override the stubbed methods."""
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
    """Defines a temperature reading taken by a sensor at a specific time."""
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


class Accuweather(Sensor):
    """A sensor class representing an outdoor temperature 
    fetched from Accuweather."""
    __tablename__ = 'accuweather'
    __mapper_args__ = {'polymorphic_identity':'accuweather'}
    
    id = Column(Integer, ForeignKey('sensor.id'), primary_key=True)
    loccode = Column(String(10), nullable=False)
    
    def __init__(self,loccode,name=None,description=None):
        self.loccode = loccode
        if name is None:
            name = 'Accuweather {}'.format(loccode)
        super().__init__(name,description)
    
    def __repr__(self):
        return "<Accuweather({0})>".format(self.loccode)
    
    def read(self):
        url='http://rss.accuweather.com/rss/liveweather_rss.asp'
        data = {'metric':0,'locCode':self.loccode}
        with urlopen(url+'?'+urlencode(data)) as response:
            xml = response.read()
        docroot = ET.fromstring(xml)
        currentweather = docroot.find('channel').find('item').find('title').text
        temp = float(re.findall(r'\d+', currentweather)[0])
        time = datetime.now()
        return Reading(time,temp,self)
    
    def available(self):
        try:
            self.read()
        except:
            return False
        else:
            return True


class W1Therm(Sensor):
    """A sensor class representing a 1-wire temperature sensor,
    e.g. DS18b20 
    Uses the w1thermsensor package for the heavy lifting.
    Source: https://github.com/timofurrer/w1thermsensor"""
    __tablename__ = 'w1therm'
    __mapper_args__ = {'polymorphic_identity':'w1therm'}

    id = Column(Integer, ForeignKey('sensor.id'), primary_key=True)
    w1_type = Column(Integer, nullable=False)
    w1_id = Column(String(16), nullable=False)
    
    def __init__(self,w1_type,w1_id,name=None,description=None):
        self.w1_type = w1_type
        self.w1_id = w1_id
        if name is None:
            name = 'W1Therm {0}'.format(w1_id)
        super().__init__(name, description)
    
    def __repr__(self):
        return "<W1Therm('{0}','{1}')>".format(
                    hex(self.w1_type)[2:],
                    self.w1_id)
    
    def available(self):
        try:
            wts = W1ThermSensor(sensor_type=self.w1_type,sensor_id=self.w1_id)
        except NoSensorFoundError:
            return False
        else:
            return True
    
    def read(self):
        wts = W1ThermSensor(sensor_type=self.w1_type,sensor_id=self.w1_id)
        temp = wts.get_temperature(W1ThermSensor.DEGREES_F)
        time = datetime.now()
        return Reading(time,temp,self)

