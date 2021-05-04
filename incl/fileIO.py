import sys
from os import access, R_OK, F_OK, W_OK
from os.path import isfile

from incl.logging import *

def fileExists(filename):
    retval = False

    if isfile(filename) and access(filename, R_OK):
        retval = True

    return retval


def fileRead(filename,logger=None):
    file_ok = True
    source = ""

    if (access(filename,F_OK) == False):
        if logger != None:
            logger.showError("{}: {} '{}' not found".format(
                "Error Occurred","File",filename),-1)
        file_ok = False

    if file_ok == True:
        if (access(filename,R_OK) == False):
            if logger != None:
                logger.showError("{}: {} '{}' {}".format(
                    "Error Occurred","File",filename,
                    "not readable"),-1)
            file_ok = False

    if file_ok == True:
        if logger != None:
            logger.logMessage("READING FILE: {}".format(
                filename))

    if file_ok == True:
        try:
            filevar = open(filename,"r")
            source = filevar.read()
        except IOError as err:
            source = None
            if logger != None:
                logger.showError("{}: I/O error({}): {}".format(
                    "Error Occurred",err.errno,err.strerror),1,False)
        except:
            source = None
            if logger != None:
                logger.showError("{}: {}: {}".format(
                    "Error Occurred","Unexpected error",
                    sys.exc_info(),1,False))

    return source


def fileWrite(filename,string,binary=False,logger=None):
    retval = False
    file_ok = True

    if (fileExists(filename) and access(filename,W_OK) == False):
        logger.showError("{}: {} '{}' not writable".format(
            "Error Occurred","File",filename),-1)
        file_ok = False

    if file_ok == True:
        if logger != None:
            logger.logMessage("WRITING FILE: {}".format(filename))
        try:
            if binary == False:
                filevar = open(filename,"w")
            else:
                filevar = open(filename,"wb")
            filevar.write(string)
            filevar.close()

            retval = True
        except IOError as err:
            if logger != None:
                logger.showError("{}: I/O error({}): {}".format(
                    "Error Occurred",err.errno,err.strerror),1,False)
        except:
            if logger != None:
                logger.showError("{}: Unexpected error: {}".format(
                    "Error Occurred",sys.exc_info(),1,False))

    return retval
