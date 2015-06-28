from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String
from urllib.parse import urlencode
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from w1thermsensor.core import W1ThermSensor,NoSensorFoundError

from .core import Sensor, Reading

class Accuweather(Sensor):
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

