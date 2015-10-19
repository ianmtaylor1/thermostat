""" Module containing code (entry point and helper functions) for the
    manage-sensors utility."""

import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import argparse

from thermostat.sensor import Sensor,SensorGroup,Accuweather,W1Therm
from thermostat.config import Config

Session = sessionmaker()

def listsensors(args):
    """Get list of all sensors"""
    session = Session()
    groups = session.query(SensorGroup).all()
    groupless = session.query(Sensor).filter(Sensor.group_id == None).all()
    foundsensors = False
    # Print list of all sensors by group
    sensorstring="    id={id}, '{name}' {avail}"
    for g in groups:
        print("id={0} {1}:".format(g.id,g.name))
        if len(g.sensors)>0:
            foundsensors = True
            for s in g.sensors:
                available = 'Available ' if s.available() else ''
                print(sensorstring.format(id=s.id,name=s.name,avail=available))
        else:
            print("    None")
    if len(groupless)>0:
        foundsensors = True
        print("No Group:")
        for s in groupless:
            available = 'Available ' if s.available() else ''
            print(sensorstring.format(id=s.id,name=s.name,avail=available))
    if foundsensors==False:
        print("No sensors or groups.")

def add_accuweather(args):
    """Add an accuweather sensor to the database."""
    sensor = Accuweather(args.zipcode,name=args.name,description=args.description)
    session = Session()
    confirmformat = "Name: {0}\nDescription: {1}\nLocation Code: {2}\n"
    print(confirmformat.format(sensor.name,sensor.description,sensor.loccode))
    if args.yes==True or input("Add this sensor? [Y/N] ").lower() == 'y':
        session.add(sensor)
        session.commit()
    else:
        print("Abort.")
    
def add_w1therm(args):
    """Add a W1Therm sensor to the database."""
    sensor = W1Therm(args.type,args.id,name=args.name,description=args.description)
    session = Session()
    confirmformat = "Name: {0}\nDescription: {1}\nW1 Type: {2}\nW1 ID: {3}\n"
    print(confirmformat.format(sensor.name,sensor.description,sensor.w1_type,sensor.w1_id))
    if args.yes==True or input("Add this sensor? [y/n] ").lower()=='y':
        session.add(sensor)
        session.commit()
    else:
        print("Abort.")

def add_group(args):
    """Add a Sensor Group to the database."""
    group = SensorGroup(args.name, description=args.description)
    session = Session()
    confirmformat = "Name: {0}\nDescription: {1}\n"
    print(confirmformat.format(group.name,group.description))
    if args.yes==True or input("Add this sensor? [y/n] ").lower()=='y':
        session.add(group)
        session.commit()
    else:
        print("Abort.")

def change_group(args):
    """Change the group to which a sensor belongs."""
    session = Session()
    # Get the sensor and group specified
    sensorquery = session.query(Sensor).filter_by(id=args.sensorid)
    if sensorquery.count()==0:
        raise Exception('No sensors found with id={0}'.format(args.sensorid))
    elif sensorquery.count()>1:
        raise Exception('Multiple sensors found with id={0}'.format(args.sensorid))
    sensor = sensorquery.all()[0]
    if args.groupid is None:
        newgroup = None
    else:
        groupquery = session.query(SensorGroup).filter_by(id=args.groupid)
        if groupquery.count()==0:
            raise Exception('No groups found with id={0}'.format(args.sensorid))
        elif groupquery.count()>1:
            raise Exception('Multiple groups found with id={0}'.format(args.sensorid))
        newgroup = groupquery.all()[0]
    # Get confirmation and make change
    oldgroupname = None if sensor.group is None else sensor.group.name
    newgroupname = None if newgroup is None else newgroup.name
    confirmformat = "Sensor: {0}\nOld Group: {1}\nNew Group: {2}\n"
    print(confirmformat.format(sensor.name,oldgroupname,newgroupname))
    if args.yes==True or input("Change this sensor's group? [y/n] ").lower() == 'y':
        sensor.group = newgroup
        session.commit()
    else:
        print("Abort.")

def readsensor(args):
    """Read the supplied sensor and output the result."""
    session = Session()
    # Find the sensor and read it
    sensorquery = session.query(Sensor).filter_by(id=args.sensorid)
    if sensorquery.count()==0:
        raise Exception('No sensors found with id={0}'.format(args.sensorid))
    elif sensorquery.count()>1:
        raise Exception('Multiple sensors found with id={0}'.format(args.sensorid))
    sensor = sensorquery.all()[0]
    reading = sensor.read()
    # Output the results
    print("id={id}, '{name}'".format(id=sensor.id,name=sensor.name))
    print("Time: {dt}".format(dt=reading.time.strftime('%Y-%m-%d %H:%M:%S')))
    print("Value: {v:4.1f}".format(v=reading.value))
    # If 'save' is set, save the reading
    if args.save==True:
        session.commit()
        print("Saved to database.")


def main(cmdline=None):
    """Main entry point."""
    # Set up command line parser
    parser = argparse.ArgumentParser(prog='manage-sensors',description='Manage the sensors in the database')
    parser.add_argument('-c','--config',help='Configuration file path',default='thermostat.conf',dest='configfile',metavar='filename')
    parser.add_argument('-y','--yes',action='store_true',help='Answer "yes" to all prompts')
    main_subparsers = parser.add_subparsers()
    
    parser_list = main_subparsers.add_parser('list',description='List all sensors organized by group',help='List all sensors organized by group')
    parser_list.set_defaults(func=listsensors)
    
    parser_add = main_subparsers.add_parser('addsensor',description='Add a sensor to the database',help='Add a sensor')
    parser_add.add_argument('-n','--name')
    parser_add.add_argument('-d','--description')
    add_subparsers = parser_add.add_subparsers(help='Type of sensor to add')
    
    parser_aw = add_subparsers.add_parser('accuweather',description='Add an Accuweather sensor to the database',help='Add Accuweather sensor')
    parser_aw.add_argument('zipcode',help='ZIP Code for Accuweather sensor')
    parser_aw.set_defaults(func=add_accuweather)
    
    parser_w1 = add_subparsers.add_parser('w1therm',description='Add a W1Therm sensor to the database',help='Add W1Therm sensor')
    parser_w1.add_argument('type',type=int)
    parser_w1.add_argument('id')
    parser_w1.set_defaults(func=add_w1therm)
    
    parser_addgroup = main_subparsers.add_parser('addgroup',description='Add a sensor group to the database',help='Add a sensor group')
    parser_addgroup.add_argument('name')
    parser_addgroup.add_argument('-d','--description')
    parser_addgroup.set_defaults(func=add_group)
    
    parser_changegroup = main_subparsers.add_parser('changegroup',description="Change a sensor's assigned group. Leave groupid blank to remove its group.",help="Change a sensor's group")
    parser_changegroup.add_argument('sensorid',type=int,help='ID of the sensor to modify')
    parser_changegroup.add_argument('groupid',nargs='?',default=None,type=int,help="ID of the sensor's new group (blank for none)")
    parser_changegroup.set_defaults(func=change_group)
    
    parser_readsensor = main_subparsers.add_parser('readsensor',description="Take a reading from a sensor",help="Read a sensor's value")
    parser_readsensor.add_argument('sensorid',type=int,help='ID of the sensor to be read')
    parser_readsensor.add_argument('-s','--save',action='store_true',help='Save the reading to the database')
    parser_readsensor.set_defaults(func=readsensor)
    
    if cmdline is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(cmdline)

    # Get the config file name from command line
    defaultfile = 'thermostat.conf.defaults'
    config = Config(args.configfile,defaultfile)
    # Create engine and bind session
    cxn = config.option('connection')
    echo = config.option('debug/echosql',Config.BOOL)
    engine = create_engine(cxn,echo=echo)
    Session.configure(bind=engine)
    # Check what the command is and call appropriate function
    args.func(args)
    return 0
