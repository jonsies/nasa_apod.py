import os
import sys

def getOptionDefault(options,option_name):
    retval = ""

    for opt,val in options:
        if opt.lower() == option_name.lower():
            retval = val

    return retval


def getHelpText(script_name,script_version,defaults=[]):
    script_python = os.path.basename(
            "".join(sys.executable.split("/")[-1:]))

    help_text = ["Usage: {} {} [OPTION]...".format(script_python,script_name),
            "",
            "Mandatory arguments to long options are mandatory for short options too.",
            "",
            "Options:",
            "  --conf-file=\"FILE\"           configuration file to read on application",
            "                                 start to set options",
            "                                 default: \"{}\"".format(getOptionDefault(defaults,"conf_file")),
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
            "                                 default: \"{}\"".format(getOptionDefault(defaults,"image_name")),
            "  -n, --no-update              do not request APOD from url, instead use",
            "                                 prior APOD image file to set as",
            "                                 wallpaper",
            "  -r, --random                 request APOD of a random past date",
            "                                 ignored if --date option is used",
            "  -R, --response-file=\"FILE\"   set response file name for saving response",
            "                                 file",
            "                                 default: \"{}\"".format(getOptionDefault(defaults,"response_file")),
            "                                 see --save-response option",
            "  -s, --save-only              request and save APOD but do not set",
            "                                 wallpaper",
            "  -S, --save-response          flag to enable saving of request response",
            "                                 to response file",
            "                                 see --response-file option",
            "  -u, --url                    URL of APOD site",
            "                                 default: \"{}\"".format(getOptionDefault(defaults,"url")),
            "  -v, --verbose                enable verbose mode",
            "  -h, --help                   display this help and exit",
            "  --version                    output version information and exit",
            "",
            "  Example: {} {} -v -i\"wallpaper\" --date=20210429".format(script_python,script_name),
            "",
            "https://github.com/jonsies/nasa_apod.py"
            ]

    return help_text
