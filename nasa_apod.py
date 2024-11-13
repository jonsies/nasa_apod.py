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
from incl.file_io import *
from incl.progress import *

from incl.options_info import *
from incl.help_info import *


logger = None
script_version = ".057"


def getRandomDate(floor_date,ceil_date=""):
    if ceil_date == "":
        date_ceil_date = datetime.now()
    else:
        date_ceil_date = datetime.strptime(
                ceil_date,"%Y%m%d")

    date_floor_date = datetime.strptime(
            floor_date,"%Y%m%d")

    random_date = date_floor_date + \
            (date_ceil_date - date_floor_date) * \
            random.random()

    return random_date


def checkDate(date_string,floor_date,ceil_date=""):
    retval = ""

    if ceil_date == "":
        date_ceil_date = datetime.now()
    else:
        date_ceil_date = datetime.strptime(
                ceil_date,"%Y%m%d")

    date_floor_date = datetime.strptime(
            floor_date,"%Y%m%d")

    try:
        date = datetime.strptime(date_string,"%Y%m%d")
        if date < date_floor_date or date > date_ceil_date:
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


def urlRequest(url,default_blocksize=8192):
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
        blocksize = max(default_blocksize, con_length//100)
    else:
        blocksize = default_blocksize;

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
        print_prefix = "{}: [MSG] - Downloading content ".format(
                sys.argv[0])
    else:
        print_prefix = "{}: Downloading content ".format(
                sys.argv[0])

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
            logger.logMessage("{}\\DESKTOP WALLPAPER KEY".format(
                "UPDATING HKCU\\CONTROL PANEL"))
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

    source = None

    apod_floor_date = "19950620"
    apod_page_ext = "html"
    apod_regex_pattern = "href=\"image.+?\\..{3}"
    apod_regex_lstrip = "href=\""
    apod_regex_rstrip = ""

    opt_ignored_default_options = ["conf_file",
            "conf_write_defaults","version","help"]

    logger = pyLogging(sys.argv[0])

    options = getOptions()
    s_opts = pyOptions(sys.argv[0],script_version,
            options,"conf_file")

    help_text = getHelpText(sys.argv[0],script_version,
            [
                ["conf_file",s_opts.getDefaultOption("conf_file")],
                ["image_name",s_opts.getDefaultOption("image_name")],
                ["response_file",s_opts.getDefaultOption(
                    "response_file")],
                ["url",s_opts.getDefaultOption("url")],
            ])

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
    opt_apod_last_file = s_opts.getOption("apod_last_file")

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
        date_string = checkDate(opt_date,apod_floor_date)
        if date_string == "":
            logger.showError(
                    "{}: date option value invalid ({})".format(
                        "Error Occurred",opt_date))

        date_url = "{}{}{}.{}".format(opt_url,"ap",date_string,
                apod_page_ext)
        date_string = None

    elif opt_random == True:
        date = getRandomDate(apod_floor_date)
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

                logger.printMessage("Image saved: {}".format(
                    image_file_name))

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
            s_opts.setOption("apod_last_file",image_file_name)
            s_opts.writeOptions(["apod_last_file"],
                    opt_ignored_default_options)

        else:
            logger.showError("{}: Image file not found ({})".format(
                "Error Occurred",image_file_name))

    logger.printMessage("Done.")



if __name__ == "__main__":
    main()
