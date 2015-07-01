""" Module containing code (entry point and helper functions) for the
    manage-sensors utility."""

import sys
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from thermostat.sensor import Sensor,SensorGroup,Accuweather,W1Therm

Session = sessionmaker()

def main(argv): 
    """Main entry point.
    argv = command-line arguments passed to utility"""
    # Check that a command was passed
    if len(argv) == 1:
        print("Must pass a command.",file=sys.stderr)
        return 1
    # Get the config file name from command line
    conffile = 'thermostat.ini'
    config = ConfigParser()
    config.read(conffile)
    # Create engine and bind session
    cxn = config['connection']
    engine = create_engine(cxn['connect string'],echo=cxn.getboolean('debug sql'))
    Session.configure(bind=engine)
    # Check what the command is and call appropriate function
    if argv[1] == 'list':
        listall()
    else:
        print("Unknown command: {0}".format(argv[1]),file=sys.stderr)
        return 1
    return 0

def listall():
    # Get list of all sensors
    session = Session()
    groups = session.query(SensorGroup).all()
    groupless = session.query(Sensor).filter(Sensor.group_id == None).all()
    # Print list of all sensors by group
    for g in groups:
        print("{0}:".format(g.name))
        if len(g.sensors)>0:
            for s in g.sensors:
                available = 'Available ' if s.available() else ''
                print("    id={0} '{1}' {2}".format(s.id,s.name,available))
        else:
            print("    None")
    print("No Group:")
    if len(groupless)>0:
        for s in groupless:
            available = 'Available ' if s.available() else ''
            print("    id={0} '{1}' {2}".format(s.id,s.name,available))
    else:
        print("    None")
