""" Module containing code (entry point and helper functions) for the
    manage-sensors utility."""

import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from thermostat.sensor import Sensor,SensorGroup,Accuweather,W1Therm
from thermostat.config import Config

Session = sessionmaker()

def listsensors():
    # Get list of all sensors
    session = Session()
    groups = session.query(SensorGroup).all()
    groupless = session.query(Sensor).filter(Sensor.group_id == None).all()
    foundsensors = False
    # Print list of all sensors by group
    for g in groups:
        print("{0}:".format(g.name))
        if len(g.sensors)>0:
            foundsensors = True
            for s in g.sensors:
                available = 'Available ' if s.available() else ''
                print("    id={0} '{1}' {2}".format(s.id,s.name,available))
        else:
            print("    None")
    if len(groupless)>0:
        foundsensors = True
        print("No Group:")
        for s in groupless:
            available = 'Available ' if s.available() else ''
            print("    id={0} '{1}' {2}".format(s.id,s.name,available))
    if foundsensors==False:
        print("No sensors or groups.")
    return 0

def usage():
    print("Usage:")
    print("manage-sensors list")

def main(argv): 
    """Main entry point.
    argv = command-line arguments passed to utility"""
    # Get the config file name from command line
    conffile = 'thermostat.conf'
    defaultfile = 'thermostat.conf.defaults'
    config = Config(conffile,defaultfile)
    # Create engine and bind session
    cxn = config.option('connection')
    echo = config.option('debug/echosql',Config.BOOL)
    engine = create_engine(cxn,echo=echo)
    Session.configure(bind=engine)
    # Check what the command is and call appropriate function
    commands = {'list':listsensors}
    try:
        if len(argv) > 2:
            opts = argv[2:]
        else:
            opts = []
        return commands[argv[1]](*opts)
    except Exception as e:
        print(e.__class__.__name__,':',e,end='\n\n')
        usage()
        return 1
