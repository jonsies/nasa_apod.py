import sys
import os
import getopt

from incl.fileIO import *
from incl.logging import *

class pyOptions:
    TYPE_BOOL = 0
    TYPE_INT = 1
    TYPE_FLOAT = 2
    TYPE_STRING = 3

    def __init__(self,script_name,script_version,
            options,conf_file_option):

        # self.options syntax:
        #
        # ["options_name",
        #   "short_opt","long_opt",has_arguments,
        #   default_value,
        #   type,lowerbound,upperbound]
        #
        # 0 = options_name
        # 1 = short_opt
        # 2 = long_opt
        # 3 = has_arguments
        # 4 = default_value
        # 5 = type (0: bool, 1: int, 2: float, 3: string)
        # 6 = lowerbound (OPTIONAL: if int or float)
        # 7 = upperbound (OPTIONAL: if int or float)

        self.__script_name = script_name
        self.__script_version = script_version
        self.__options = options
        self.__conf_file_option = conf_file_option

        self.__script_python = os.path.basename(
                "".join(sys.executable.split("/")[-1:]))

        self.__values = [None] * len(options)
        self.__parameters = []

        self.__short_options = ""
        self.__long_options = ""
        self.__help_text = "<help text here>"

        self.__initOptions()
        self.__setDefaults()

        self.logger = pyLogging(self.__script_name)


    def setLogger(self,pyLog):
        self.logger = pyLog


    def setHelpText(self,help_text):
        self.__help_text = ""
        for line in help_text:
            self.__help_text += line + "\n"
        self.__help_text = self.__help_text.rstrip(" \n")


    def getParameters(self):
        return self.__parameters


    def getOption(self,option_name):
        retval = None

        for i in range(0,len(self.__options),1):
            if self.__options[i][0].lower() == option_name.lower():
                retval = self.__values[i]

        return retval


    def getDefaultOption(self,option_name):
        retval = None

        for opt in self.__options:
            if opt[0].lower() == option_name.lower():
                retval = opt[4]

        return retval


    def setOption(self,option_name,value):
        value_set = False

        for i in range(0,len(self.__options),1):
            if self.__options[i][0].lower() == option_name.lower():
                self.__values[i] = value
                value_set = True

        if value_set == False:
            self.logger.showError("{}: {} recognized ({})".format(
                "Error Occurred","Option name not",option_name),-1)


    def writeDefaultOptions(self,ignore_options):
        config_string = "" 
        filename = self.getOption(self.__conf_file_option)

        for opt in self.__options:
            if opt[0] not in ignore_options:
                config_string += "{} {}\n".format(
                        opt[0],opt[4])

        fileWrite(filename,config_string,logger=self.logger)


    def writeOptions(self,write_options,ignore_options):
        config_string = ""
        option_list = [] 
        filename = self.getOption(self.__conf_file_option)

        config_list = fileRead(filename,self.logger).split("\n")

        for line in config_list:
            cur_line = line.replace("\t"," ").split(" ")
            if cur_line[0] != "" and cur_line[0][0] != "#" \
                    and cur_line[0][0].strip(" ") != "\n":
                option = cur_line[0].lower()

                if option in write_options \
                        and option not in ignore_options:
                    value = self.getOption(
                            write_options[write_options.index(
                                option)])

                else:
                    option_list.append([line,""])
            elif cur_line[0] != "" and cur_line[0][0] == "#":
                option_list.append([line,""])


        for option in write_options:
            value = self.getOption(
                    write_options[write_options.index(option)])
            option_list.append([option,value])

        for option,value in option_list:
            if option[0] == "#" or option not in write_options:
                config_string += "{}\n".format(option)
            else:
                config_string += "{} {}\n".format(option,value)

        fileWrite(filename,config_string,logger=self.logger)



    def __setDefaults(self):
        for i in range(0,len(self.__options),1):
            self.__values[i] = self.__options[i][4]


    def __unQuoteStr(self,value):
        retval = value

        value = str(value)
        if len(value) > 1:
            if value[0] == "\"" and value[-1] == "\"":
                retval = value[1:-1]
            elif value[0] == "'" and value[-1:] == "'":
                retval = value[1:-1]

        return retval


    def __convertOptionToBool(self,value):
        retval = False

        if value.lower() == "false":
            retval = False
        elif value == "" or value.lower() == "true":
            retval = True

        return retval


    def __convertOptionToInt(self,value,option,
            lowerbound = "",upperbound = ""):
        try:
            i = int(value)
            if lowerbound != "" and i < lowerbound:
                self.logger.showError("{}:  Option {} {}".format(
                    "Error Occurred",option,
                    "value out of bounds"),2,True)
            elif upperbound != "" and i > upperbound:
                self.logger.showError("{}:  Option {} {}".format(
                    "Error Occurred",option,
                    "value out of bounds"),2,True)
            return i
        except ValueError as err:
            self.logger.showError("{}: {} {}: {}".format(
                "Error Occurred","Error with option",
                option,str(err)),2,True)


    def __convertOptionToFloat(self,value,option,
            lowerbound = "",upperbound = ""):
        try:
            i = float(value)
            if lowerbound != "" and i < lowerbound:
                self.logger.showError("{}:  Option {} {}".format(
                    "Error Occurred",option,
                    "value out of bounds"),2,True)
            elif upperbound != "" and i > upperbound:
                self.logger.showError("{}:  Option {} {}".format(
                    "Error Occurred",option,
                    "value out of bounds"),2,True)
            return i
        except ValueError as err:
            self.logger.showError("{}: {} {}: {}".format(
                "Error Occurred","Error with option",
                option,str(err)),2,True)


    def __getOptionName(self,option):
        retval = None

        for opt in self.__options:
            if "-" + opt[1] == option or \
                    "--" + opt[2] == option:
                retval = opt[0].lower()
                break

        return retval


    def __initOptions(self):
        short_options = ""
        long_options = []

        for opt in self.__options:
            if opt[1] != "":
                temp_option = opt[1]
                if opt[3] == True:
                    temp_option = temp_option + ":"

                short_options = short_options + temp_option

            if opt[2] != "":
                temp_option = opt[2]
                if opt[3] == True:
                    temp_option = temp_option + "="

                long_options = long_options + [temp_option]


        self.__short_options = short_options
        self.__long_options = long_options


    def __parseInitOption(self,option,value):
        if option == "version":
            self.__printVersion()
            sys.exit(0)
        elif option == "verbose":
            self.setOption("verbose",True)
        elif option == "help":
            self.__printHelp()


    def __initVerbose(self,argcount):
        self.logger.verbose = True
        self.logger.logMessage("INIT: {}".format(self.__script_name))
        self.logger.logMessage("BUILD: {}".format(self.__script_version))
        self.logger.logMessage("VERBOSE OUTPUT ENABLED")
        self.logger.logMessage("ARGUMENT COUNT: {}".format(argcount))
        self.logger.logMessage("---")



    def __parseOption(self,option,value):
        for i in range(0,len(self.__options),1):
            if option == self.__options[i][0]:
                lowerbound = ""
                upperbound = ""
                if (len(self.__options[i]) >= 7):
                    lowerbound = self.__options[i][6]
                if (len(self.__options[i]) >= 8):
                    upperbound = self.__options[i][7]

                if self.__options[i][5] == pyOptions.TYPE_BOOL:
                    self.__values[i] = \
                            self.__convertOptionToBool(value)
                    break
                elif self.__options[i][5] == pyOptions.TYPE_INT:
                    self.__values[i] = \
                            self.__convertOptionToInt(value,option,
                                    lowerbound,upperbound)
                    break
                elif self.__options[i][5] == pyOptions.TYPE_FLOAT:
                    self.__values[i] = \
                            self.__convertOptionToFloat(value,option,
                                    lowerbound,upperbound)
                    break
                elif self.__options[i][5] == pyOptions.TYPE_STRING:
                    self.__values[i] = self.__unQuoteStr(value)
                    break



    def __parseArgument(self,argument,value):
        option = self.__getOptionName(argument)

        if option != "": 
            self.__parseOption(option,value)
        else:
            self.logger.showError("{}: {} recognized ({})".format(
                "Error Occurred","Argument not",argument),-1)


    def __printVersion(self):
        print("{} {}".format(self.__script_name,
            self.__script_version))


    def __printHelp(self):
        self.__printVersion()
        self.__setDefaults()
        print(self.__help_text)

        sys.exit(0)


    def __parseArguments(self,args,init_flag=False):
        try:
            opts, args = getopt.gnu_getopt(args[1:],
                    self.__short_options,self.__long_options)
        except getopt.GetoptError as err:
            self.logger.showError("{}: {}".format(
                "Error Occurred",str(err),2,True))

        self.args = " ".join(args).strip()

        if self.args == "?":
            self.__printHelp()

        if init_flag == True:
            for o, v in opts:
                self.__parseInitOption(self.__getOptionName(o),v)

        if init_flag == False:
            for o, v in opts:
                if v == "":
                    self.logger.logMessage(
                            "PARSING ARGUMENT: {}".format(o))
                else:
                    self.logger.logMessage(
                            "PARSING ARGUMENT: {} : {}".format(
                        o,v))
                self.__parseArgument(o,v)

            self.__parameters = args
            for o in args:
                self.logger.logMessage(
                        "PARSING PARAMETER: {}".format(o))


    def __parseConfigFileArguments(self,args):
        try:
            opts, args = getopt.gnu_getopt(args[1:],
                    self.__short_options,self.__long_options)
        except getopt.GetoptError as err:
            self.logger.showError("{}: {}".format(
                "Error Occurred",str(err),2,True))

        self.args = " ".join(args).strip()

        for argument, value in opts:
            argument = argument.strip(" \t")
            value = value.strip(" \t")
            option = self.__getOptionName(argument)

            if option == self.__conf_file_option:
                self.setOption(self.__conf_file_option,value)

                self.logger.logMessage(
                        "PARSING CONFIG: {} : {}".format(
                    argument,value))


    def __readOptionConfigFile(self,conf_filename):
        config_list = []

        config_list = fileRead(conf_filename,self.logger).split("\n")

        for line in config_list:
            cur_line = line.replace("\t"," ").split(" ")
            if cur_line[0] != "" and cur_line[0][0] != "#" \
                    and cur_line[0][0].strip(" ") != "\n":
                option = cur_line[0].lower()
                value = " ".join(cur_line[1:]).strip(" \n")

                if value == "":
                    self.logger.logMessage(
                            "PARSING CONFIG: {}".format(option))

                else:
                    self.logger.logMessage(
                            "PARSING CONFIG: {} : {}".format(
                                option,value))

                self.__parseOption(option,value)


    def readOptions(self,arguments):
        self.__parseArguments(arguments,True)
        if self.getOption("verbose") == True:
            self.__initVerbose(len(arguments)-1)
        self.__parseConfigFileArguments(arguments)
        self.__readOptionConfigFile(
                self.getOption(self.__conf_file_option))
        self.__parseArguments(arguments)

        self.__printOptions()


    def __printOptions(self):
        self.logger.logMessage("---")
        self.logger.logMessage("OPTIONS:")

        for i in range(0,len(self.__options),1):
            option_name = self.__options[i][0]

            if option_name.lower() != "help" and \
                    option_name.lower() != "version":
                option_value = self.__values[i]
                self.logger.logMessage("{}: {}".format(
                    option_name.upper(),option_value))

        self.logger.logMessage("---")
