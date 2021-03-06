from thermostat.sensor import Base
from thermostat.config import Config

from sqlalchemy import create_engine
import argparse

def main(cmdline=None):
    # Parse the command line arguments
    parser = argparse.ArgumentParser(prog='initdb',description="Initialize the database for the thermostat backend.")
    parser.add_argument('-c','--config',help='Configuration file path',default='thermostat.conf',dest='configfile',metavar='filename')
    parser.add_argument('-y','--yes',action='store_true',help='Answer "yes" to all prompts')
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
    # Check which tables are already there
    mdtables = [x for x in Base.metadata.tables]
    enginetables = engine.table_names()
    existing,new = [],[]
    for t in mdtables:
        if t in enginetables:
            existing.append(t)
        else:
            new.append(t)
    # Confirm table creations
    confirmstring = 'Tables in engine: {0}\nTables to create: {1}\n'
    print(confirmstring.format(','.join(existing),','.join(new)))
    if len(new) > 0:
        # Boolean short-circuit: only prompts if not args['yes']
        if args.yes==True or input('Continue? [y/n] ').lower() == 'y':
            Base.metadata.create_all(engine)
            print('Done.')
        else:
            print('Abort.')
    else:
        print('No tables to create.')
    return 0

