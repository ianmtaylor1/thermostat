"""Module that holds classes, variables, and functions related to processing
the thermostat configuration file."""

import xml.etree.ElementTree as ET

class OptionNotFound(Exception):
    """Exception raised when a configuration option is not found."""
    def __init__(self,optionname):
        self.optionname = optionname
    def __str__(self):
        return "Option '{0}' not found, no default available".format(self.optionname)


class OptionTypeError(Exception):
    """Exception raised when there is an error in parsing the option
    to its datatype."""
    def __init__(self,optionname,typename):
        self.optionname = optionname
        self.typename = typename
    def __str__(self):
        return "Error converting '{0}' to type '{1}'".format(self.optionname,self.typename)


def _strtobool(string):
    """A function to convert strings to boolean in a more human-intuitive
    way than the standard 'bool' function."""
    s = string.lower()
    try:
        i = int(s)
    except:
        i = None
    if (s=='true') or (s=='yes') or (s=='t') or (s=='y') or (i==1):
        return True
    elif (s=='false') or (s=='no') or (s=='f') or (s=='n') or (i==0):
        return False
    else:
        raise TypeError()


class Config():
    """Class to read in a configuration file and retrieve options. It should
    fall back to defaults when no option is in the main file."""
    
    # Constants defining data types
    STRING = 'string'
    INT = 'integer'
    FLOAT = 'float'
    BOOL = 'bool'
    _TYPECONV = {STRING:lambda x:x,
                 INT:int,
                 FLOAT:float,
                 BOOL:_strtobool}

    def __init__(self,mainfile,defaultfile=None):
        self._main = ET.parse(mainfile)
        if defaultfile is None:
            self._default = None
        else:
            self._default = ET.parse(defaultfile)
    
    def option(self,name,dtype=STRING):
        """ Returns a single option by the given name (optionally) converted
        to the given type."""
        element = self._main.find(name)
        if (element is None) and (self._default is not None):
            element = self._default.find(name)
        if element is None:
            raise OptionNotFound(name)
        try:
            return self._TYPECONV[dtype](element.text)
        except:
            raise OptionTypeError(name,dtype)
    
    def optionlist(self,name,dtype=STRING):
        """Returns a list of options by the given name (optionally) converted
        to the given type."""
        elements = self._main.findall(name)
        if (len(elements)==0) and (self._default is not None):
            elements = self._default.findall(name)
        if len(elements)==0:
            raise OptionNotFound(name)
        try:
            return [self._TYPECONV[dtype](e.text) for e in elements]
        except:
            raise OptionTypeError(name,dtype)
