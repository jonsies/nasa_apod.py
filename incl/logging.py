import sys
from os.path import basename

class pyLogging:

    def __init__(self,script_name):
        self.__script_python = basename(
                "".join(sys.executable.split("/")[-1:]))

        self.__script_name = script_name
        self.verbose = False

    # print message to terminal
    # disregard verbose mode
    def printMessage(self,message,msg_type="MSG"):
        if self.verbose == True:
            print("{}: [{}] - {}".format(self.__script_name,
                msg_type,message))
        else:
            print("{}: {}".format(self.__script_name,message))

    # print log
    def printLog(self,logtype,message):
        print("{}: [{}] - {}".format(
            self.__script_name,logtype,message))

    def printHelpMessage(self):
        print("Try '{} {} --help' for more information.".format(
            self.__script_python,self.__script_name))


    # debug message
    def debugMessage(self,message):
        self.printLog("DEBUG",message)

    # logging to terminal taking into account
    # verbose mode
    def logMessage(self,message):
        if self.verbose == True:
            self.printLog("LOG",message)

    # logs passed string as error message to terminal
    # if exitcode is >= 0, scripts exit with exitcode as status
    # if helpflag = True, the help flag tip is shown
    def showError(self,string,exitcode=1,helpflag=0):
        self.printMessage(string,"ERR")
        if helpflag == True:
            self.printHelpMessage()
        if exitcode >= 0:
            sys.exit(exitcode)
