""" Module containing code (entry point and helper functions) for the
    manage-sensors utility."""

import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import argparse

from thermostat.sensor import Sensor,SensorGroup,Accuweather,W1Therm
from thermostat.config import Config

Session = sessionmaker()

def listsensors():
    """Get list of all sensors"""
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

def addsensor():
    """Add a sensor to the database."""
    raise NotImplementedError('Adding sensor not implemented')


def main(): 
    """Main entry point."""
    # Set up command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument('command',choices=['list','addsensor'],
                        help='Command to run')
    parser.add_argument('-c','--config',help='Configuration file path',
                        default='thermostat.conf',dest='configfile',
                        metavar='filename')
    args = parser.parse_args()
    # Get the config file name from command line
    defaultfile = 'thermostat.conf.defaults'
    config = Config(args.configfile,defaultfile)
    # Create engine and bind session
    cxn = config.option('connection')
    echo = config.option('debug/echosql',Config.BOOL)
    engine = create_engine(cxn,echo=echo)
    Session.configure(bind=engine)
    # Check what the command is and call appropriate function
    if args.command == 'list':
        return listsensors()
    elif args.command == 'addsensors':
        return addsensor()
    else:
        return 255

