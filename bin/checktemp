#!/usr/bin/env python3

#Test script to check the temperature using a DS18B20

from w1thermsensor.core import W1ThermSensor, KernelModuleLoadError, NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError

sensors = W1ThermSensor.get_available_sensors()

temps = []

for s in sensors:
    t = s.get_temperature(W1ThermSensor.DEGREES_F)
    temps.append(t)
    print("Sensor {id}: {t:5.2f}\N{DEGREE SIGN}F".format(id=s.id, t=t))

print("Mean Temperature: {t:5.2f}\N{DEGREE SIGN}F".format(t=sum(temps)/len(temps)))

