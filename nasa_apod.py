import os
import sys
import io
import platform
import ctypes
import re
import random
import subprocess
from datetime import datetime
from time import time
from urllib.request import urlopen
import urllib.error

sys.dont_write_bytecode = True

from incl.options import *
from incl.logging import *
from incl.fileIO import *
from incl.progress import *


script_python = os.path.basename(
        "".join(sys.executable.split("/")[-1:]))
script_name = sys.argv[0]
script_version = ".055"
script_url = "https://github.com/jonsies/nasa_apod.py"

http_default_blocksize = 8192

apod_floor_date = "19950620"
apod_page_ext = "html"

apod_regex_pattern = "href=\"image.+?\..{3}"
apod_regex_lstrip = "href=\""
apod_regex_rstrip = ""

opt_name_apod_last_file = "apod_last_file"

opt_conf_file_default = "config"
opt_image_name_default = "apod"
opt_response_file_default = "response.txt"
opt_url_default = "https://apod.nasa.gov/apod/"

opt_ignored_default_options = ["conf_file",
        "conf_write_defaults","version","help"]

logger = None


help_text = ["Usage: {} {} [OPTION]...".format(script_python,script_name),
        "",
        "Mandatory arguments to long options are mandatory for short options too.",
        "",
        "Options:",
        "  --conf-file=\"FILE\"           configuration file to read on application",
        "                                 start to set options",
        "                                 default: \"{}\"".format(opt_conf_file_default),
        "                               passed parameters take precedence over",
        "                                 configuration values",
        "  --conf-write-defaults        write default option values to the",
        "                                 configuration file and exit",
        "  -c, --set-bg-cmd=\"CMD\"       command to use to set wallpaper for",
        "                                 *nix based systems",
        "  -d, --date=########          retrieve APOD for specific date",
        "                                 format is YYYYMMDD",
        "  -f, --force-update           disregard 24h file timestamp check and",
        "                                 force APOD download",
        "  -i, --image-name=\"NAME\"      name to use to save APOD image",
        "                                 extension not required",
        "                                 default: \"{}\"".format(opt_image_name_default),
        "  -n, --no-update              do not request APOD from url, instead use",
        "                                 prior APOD image file to set as",
        "                                 wallpaper",
        "  -r, --random                 request APOD of a random past date",
        "                                 ignored if --date option is used",
        "  -R, --response-file=\"FILE\"   set response file name for saving response",
        "                                 file",
        "                                 default: \"{}\"".format(opt_response_file_default),
        "                                 see --save-response option",
        "  -s, --save-only              request and save APOD but do not set",
        "                                 wallpaper",
        "  -S, --save-response          flag to enable saving of request response",
        "                                 to response file",
        "                                 see --response-file option",
        "  -u, --url                    URL of APOD site",
        "                                 default: \"{}\"".format(opt_url_default),
        "  -v, --verbose                enable verbose mode",
        "  -h, --help                   display this help and exit",
        "  --version                    output version information and exit",
        "",
        "  Example: {} {} -v -i\"wallpaper\" --date=20210429".format(script_python,script_name),
        "",
        "{}".format(script_url)
        ]


def getRandomDate():
    floor_date = datetime.strptime(
            apod_floor_date,"%Y%m%d")

    ceil_date = datetime.now()

    random_date = floor_date + (ceil_date - floor_date) * \
            random.random()

    return random_date


def checkDate(date_string):
    retval = ""

    floor_date = datetime.strptime(
            apod_floor_date,"%Y%m%d")
    ceil_date = datetime.now()

    try:
        date = datetime.strptime(date_string,"%Y%m%d")
        if date < floor_date or date > ceil_date:
            retval = ""
        else:
            retval = date.strftime("%y%m%d")
    except:
        retval = ""

    return retval


def humanReadableSize(bytesize):
    retval = "{}".format(bytesize)
    step = 1000

    for x in ["", "K", "M"]:
        if bytesize < step:
            retval = "{0:.2f}".format(bytesize)
            retval += "{}".format(x)
            break
        bytesize /= step

    return retval


def urlRequest(url):
    con_length = None
    con_charset = None

    logger.printMessage("Requesting URL: {}".format(url))

    try:
        response = urlopen(url)
    except urllib.error.URLError as e:
        logger.showError("{}: {}: {}".format(
            "Error Occurred","URL error",e.reason))
    except urllib.error.HTTPError as e:
        logger.showError("{}: {}: {}".format(
            "Error Occurred","HTTP error",e.reason))
    except Exception:
        logger.showError("{}: {}".format(
            "Error Occurred","Unexpected error with URL request"))

    logger.printMessage("Request complete: {} ({})".format(
        response.status,response.msg))

    con_length = response.getheader("content-length")

    con_type = response.getheader("content-type")
    if len(con_type.split(";")) > 1:
        con_charset = con_type.split(";")[1].lstrip(" charset=")
    con_type = con_type.split(";")[0]

    if con_length:
        con_length = int(con_length)
        blocksize = max(http_default_blocksize, con_length//100)
    else:
        blocksize = http_default_blocksize;

    logger.logMessage("REQUEST CONTENT-TYPE: {}".format(con_type))

    if con_charset:
        logger.logMessage("REQUEST CONTENT-CHARSET: {}".format(
            con_charset))

    if con_length:
        logger.logMessage("REQUEST CONTENT-LENGTH: {}".format(
            con_length))

    logger.logMessage("BUFFER BLOCKSIZE: {}".format(blocksize))

    if con_length:
        logger.printMessage("Requesting content ({})".format(
            humanReadableSize(con_length)))
    else:
        logger.printMessage("Requesting content")

    size = 0
    buffer = io.BytesIO()

    if logger.verbose == True:
        print_prefix = "{}: [MSG] - Downloading content: ".format(
                script_name)
    else:
        print_prefix = "{}: Downloading content: ".format(
                script_name)

    while True:
        readbuf = response.read(blocksize)
        if not readbuf:
            break

        size += len(readbuf)
        buffer.write(readbuf)

        if con_length:
            printProgress(int((size/con_length)*100),15,
                    prefix=print_prefix)

    if con_charset:
        buffer = buffer.getvalue().decode(con_charset,errors="ignore")
    else:
        buffer = buffer.getvalue()


    return buffer


def setWallpaper(image_file,set_bg_cmd):
    full_path = os.path.abspath(image_file)
    
    system = platform.system()

    logger.printMessage("Setting wallpaper for {}".format(system))
    logger.printMessage("   {}".format(full_path))

    logger.logMessage("SYSTEM PLATFORM: {}".format(system.upper()))
    
    if system == "Windows":
        import winreg
        logger.logMessage("{} {}".format(
            "SETTING USER32","SYSTEM PARAMETERS INFO W"))
        ctypes.windll.user32.SystemParametersInfoW(20,0,full_path,0)
        try:
            reg_con = winreg.ConnectRegistry(None,
                winreg.HKEY_CURRENT_USER)
            reg_key = winreg.OpenKey(reg_con,
                r"Control Panel\Desktop",0,winreg.KEY_WRITE)
            winreg.SetValueEx(reg_key,"Wallpaper",0,
                winreg.REG_SZ,full_path)
            winreg.CloseKey(reg_key)
            logger.logMessage("{}\DESKTOP WALLPAPER KEY".format(
                "UPDATING HKCU\CONTROL PANEL"))
        except WindowsError:
            logger.showError("{}: {} registry key".format(
                "Error Occurred","Windows error on setting"))

        logger.logMessage("{} {} SYSTEM PARAMETERS".format(
            "ENVOKING USER32","UPDATE PER USER"))
        ctypes.windll.user32.UpdatePerUserSystemParameters   
        
    elif system.lower() == "linux" or "bsd" in system.lower():
        shell_exec_str = "{} \"{}\"".format(set_bg_cmd,full_path)
        logger.logMessage("{}: {}".format(
            "ENVOKING COMMAND",shell_exec_str))
        subprocess.Popen(shell_exec_str,shell=True)


def main():
    global logger

    source = ""

    options = [
            ["conf_file",
                "","conf-file",True,
                opt_conf_file_default,pyOptions.TYPE_STRING],
            ["conf_write_defaults",
                "","conf-write-defaults",False,
                False,pyOptions.TYPE_BOOL],
            ["set_bg_cmd",
                "c","set-bg-cmd",True,
                "/usr/bin/feh --bg-fill",pyOptions.TYPE_STRING],
            ["date",
                "d","date",True,
                "",pyOptions.TYPE_STRING],
            ["force_update",
                "f","force-update",False,
                False,pyOptions.TYPE_BOOL],
            ["image_name",
                "i","image-name",True,
                opt_image_name_default,pyOptions.TYPE_STRING],
            ["no_update",
                "n","no-update",False,
                False,pyOptions.TYPE_BOOL],
            ["random",
                "r","random",False,
                False,pyOptions.TYPE_BOOL],
            ["response_file",
                "R","respone-file",True,
                opt_response_file_default,pyOptions.TYPE_STRING],
            ["save_only",
                "s","save-only",False,
                False,pyOptions.TYPE_BOOL],
            ["save_response",
                "S","save-response",False,
                False,pyOptions.TYPE_BOOL],
            ["url",
                "u","url",True,
                opt_url_default,pyOptions.TYPE_STRING],
            ["verbose",
                "v","verbose",False,
                False,pyOptions.TYPE_BOOL],
            [opt_name_apod_last_file,
                "","",False,
                "",pyOptions.TYPE_STRING],
            ["version",
                "","version",False,
                False,pyOptions.TYPE_BOOL],
            ["help",
                "h","help",False,
                False,pyOptions.TYPE_BOOL]
        ]


    logger = pyLogging(script_name)

    s_opts = pyOptions(script_name,script_version,
            options,"conf_file")
    s_opts.setLogger(logger)
    s_opts.setHelpText(help_text)
    s_opts.readOptions(sys.argv)

    opt_conf_file = s_opts.getOption("conf_file")
    if s_opts.getOption("conf_write_defaults") == True:
        logger.printMessage("{} configuration: {}".format(
            "Writing default",opt_conf_file))
        s_opts.writeDefaultOptions(opt_ignored_default_options)
        logger.printMessage("Exiting.")
        sys.exit(0)


    opt_url = s_opts.getOption("url")
    opt_no_update = s_opts.getOption("no_update")
    opt_force_update = s_opts.getOption("force_update")
    opt_random = s_opts.getOption("random")
    opt_date = s_opts.getOption("date")
    opt_image_name = s_opts.getOption("image_name")
    opt_response_file = s_opts.getOption("response_file")
    opt_save_response = s_opts.getOption("save_response")
    opt_save_only = s_opts.getOption("save_only")
    opt_setbg_cmd = s_opts.getOption("set_bg_cmd")
    opt_apod_last_file = s_opts.getOption(opt_name_apod_last_file)

    options = None


    file_mdelta = 24
    if opt_apod_last_file != "":
        if fileExists(opt_apod_last_file):
            logger.logMessage("IMAGE FILE EXISTS: {}".format(
                opt_apod_last_file))
            file_mdelta = (time() - \
                    os.path.getmtime(opt_apod_last_file))/60/60
            logger.logMessage("IMAGE FILE MDELTA: {0:.02f}h".format(
                file_mdelta))
        else:
            logger.logMessage("IMAGE FILE NOT FOUND: {}".format(
                opt_apod_last_file))
    else:
        logger.printMessage("Last APOD image unavailable")


    if opt_date != "":
        logger.logMessage("EXACT DATE SPECIFIED: {}".format(
            opt_date))
        date_string = checkDate(opt_date)
        if date_string == "":
            logger.showError(
                    "{}: date option value invalid ({})".format(
                        "Error Occurred",opt_date))

        date_url = "{}{}{}.{}".format(opt_url,"ap",date_string,
                apod_page_ext)
        date_string = None

    elif opt_random == True:
        date = getRandomDate()
        opt_date = datetime.strftime(date,"%Y%m%d")
        logger.logMessage("RANDOM DATE GENERATED: {}".format(
            opt_date))
        date_url = "{}{}{}.{}".format(opt_url,"ap",
            datetime.strftime(date,"%y%m%d"),apod_page_ext)
        date = None


    if opt_no_update != True:
        if opt_date != "" or opt_force_update == True or \
                file_mdelta >= 24:

            if opt_date != "":
                source = urlRequest(date_url)
            else:
                source = urlRequest(opt_url)

            if opt_save_response and source != "":
                logger.logMessage(
                        "SAVING REQUEST RESPONSE: {}".format(
                            opt_response_file))
                fileWrite(opt_response_file,source,logger=logger)

            image_url = re.search(apod_regex_pattern,source,
                    re.IGNORECASE)

            if image_url != None and image_url != "":
                image_url = image_url.group(0)
                image_url = image_url.lstrip(apod_regex_lstrip)
                image_url = image_url.rstrip(apod_regex_rstrip)

                image_file_name = "{}.{}".format(opt_image_name,
                        image_url[-3:])

                logger.printMessage("Image found: {}".format(
                    image_url))
                image_url = "{}/{}".format(
                        opt_url.rstrip("/"),image_url)

                source = urlRequest(image_url)
                fileWrite(image_file_name,source,binary=True,
                        logger=logger)

            else:
                logger.showError("{}: {}".format(
                    "Error Occurred","Could not retrieve image URL"))


        elif file_mdelta < 24:
            logger.printMessage(
                    "Last image file modified within last 24 hours")
            logger.printMessage("Skipping APOD URL request")


    if opt_save_only == False:
        if opt_no_update == True or opt_date == "" \
                and file_mdelta < 24:
            image_file_name = opt_apod_last_file;

        if image_file_name != "" and fileExists(image_file_name):
            setWallpaper(image_file_name,opt_setbg_cmd)
            s_opts.setOption(opt_name_apod_last_file,image_file_name)
            s_opts.writeOptions([opt_name_apod_last_file],
                    opt_ignored_default_options)

        else:
            logger.showError("{}: Image file not found ({})".format(
                "Error Occurred",image_file_name))

    logger.printMessage("Done.")



if __name__ == "__main__":
    main()
