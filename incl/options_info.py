from incl.options import *

def getOptions():
    options = [
            ["conf_file",
                "","conf-file",True,
                "config",pyOptions.TYPE_STRING],
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
                "apod",pyOptions.TYPE_STRING],
            ["no_update",
                "n","no-update",False,
                False,pyOptions.TYPE_BOOL],
            ["random",
                "r","random",False,
                False,pyOptions.TYPE_BOOL],
            ["response_file",
                "R","respone-file",True,
                "response.txt",pyOptions.TYPE_STRING],
            ["save_only",
                "s","save-only",False,
                False,pyOptions.TYPE_BOOL],
            ["save_response",
                "S","save-response",False,
                False,pyOptions.TYPE_BOOL],
            ["url",
                "u","url",True,
                "https://apod.nasa.gov/apod/",pyOptions.TYPE_STRING],
            ["verbose",
                "v","verbose",False,
                False,pyOptions.TYPE_BOOL],
            ["apod_last_file",
                "","",False,
                "",pyOptions.TYPE_STRING],
            ["version",
                "","version",False,
                False,pyOptions.TYPE_BOOL],
            ["help",
                "h","help",False,
                False,pyOptions.TYPE_BOOL]
        ]

    return options