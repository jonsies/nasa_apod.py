## nasa_apod.py
nasa_apod.py is a python3 script that will download NASA's astronomy picture of the day (APOD) and set it as the system wallpaper

[https://apod.nasa.gov/apod/](https://apod.nasa.gov/apod/)

- Python version 3.0 or higher required
- Built from standard python modules, no additional libraries required
- Supports and has been tested on Windows 10, Linux, and BSD

![linux](screenshots/linux.png?raw=True "Linux")
![windows](screenshots/windows.png?raw=True "Windows")


## Git

Clone the repo using the following git command:

    git clone https://github.com/jonsies/nasa_apod.py.git


## Zip Archive
 - Download the archived zip from github:
    [nasa_apod.py main head](https://github.com/jonsies/nasa_apod.py/archive/refs/heads/main.zip)
 - Extract contents of the archive with directories enabled
 - Run the script via the provided scripts from the nasa_apod.py directory:
    - Linux / BSD: `./na.sh`
    - Windows: `na.bat`
 - Or by command line by passing the script to python directly:
    - Linux / BSD: `python nasa_apod.py`
    - Windows: `python.exe nasa_apod.py`


## Execution

Running the script without any parameters will perform these tasks:

- Check for a prior APOD image
- If prior APOD image timestamp is less than 24 hours, the script will skip the request to download a new APOD image
- If prior APOD image timestamp is older than 24 hours, the script will:
    - Send a request to the main configured APOD URL
    - Parse the request response to extract the URL of the current APOD image
    - Send a request to download the current APOD image to disk
- Determine system type (ie: Windows or Linux / BSD)
- If Windows, set APOD image as desktop wallpaper
- If Linux or BSD, envoke the `set_bg_cmd` option value as a system command to set APOD image as desktop wallpaper

Various parameters can be passed to the script in order to alter script functionality. For instance you can set a specific date for the APOD, get a random date for the APOD, forego setting the wallpaper, and more.

Running the script with the `?`, `-h`, or `--help` parameter will display the help text to the terminal:

- Linux / BSD:
    - `./na.sh ?`
    - `python nasa_apod.py ?`
- Windows: 
    - `na.bat ?`
    - `python.exe nasa_apod.py ?`


## Configuration

The script checks a configuration file on execution and reads any provided options and values to modify script functionality. Each script parameter has a matching option var that can be set to change script functionality instead of passing the parameter. If a parameter is passed, it will take precedence over any configuration file values.

A specific configuration file name can be passed to the script with the `--conf-file` parameter. See the parameter section below for more information.

___NOTE:___ _The configuration file option var names and the parameter names differ slightly._

A default configuration file with all available option vars and their corresponding default values can be created by passing the parameter `--conf-write-defaults` to the script.

___NOTE:___ _This will overwrite the currently specified configuration file_

### A Note For The \*Nixes

If Linux or BSD is reported back in the python os platform call, the script uses an option var, `set_bg_cmd`, as a system command call to set the system wallpaper. Due to the large amounts of different environments available for Linux and BSD, the configuration will need to be tailored specifically for each desktop environment. The script envokes the provided value as a system command and passes the fullpath file name of the APOD image as a parameter at the end of the command.

Examples:

- xorg _(via feh)_:  
`/usr/bin/feh --bg-fill`
- xfce4:  
`xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/image-style -s 5; xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s`

The option can be set through the configuration file by adding or updating the `set_bg_cmd` option to the specific command needed in order to update the desktop wallpaper. The option can also be passed as a parameter, `set-bg-cmd`. See the parameter section below for more information.


## Parameters
```
Mandatory arguments to long options are mandatory for short options too.

Options:
  --conf-file="FILE"           configuration file to read on application
                                 start to set options
                                 default: "config"
                               passed parameters take precedence over
                                 configuration values
  --conf-write-defaults        write default option values to the
                                 configuration file and exit
  -c, --set-bg-cmd="CMD"       command to use to set wallpaper for
                                 *nix based systems
  -d, --date=########          retrieve APOD for specific date
                                 format is YYYYMMDD
  -f, --force-update           disregard 24h file timestamp check and
                                 force APOD download
  -i, --image-name="NAME"      name to use to save APOD image
                                 extension not required
                                 default: "apod"
  -n, --no-update              do not request APOD from url, instead use
                                 prior APOD image file to set as
                                 wallpaper
  -r, --random                 request APOD of a random past date
                                 ignored if --date option is used
  -R, --response-file="FILE"   set response file name for saving response
                                 file
                                 default: "response.txt"
                                 see --save-response option
  -s, --save-only              request and save APOD but do not set
                                 wallpaper
  -S, --save-response          flag to enable saving of request response
                                 to response file
                                 see --response-file option
  -u, --url                    URL of APOD site
                                 default: "https://apod.nasa.gov/apod/"
  -v, --verbose                enable verbose mode
  -h, --help                   display this help and exit
  --version                    output version information and exit

  Example: python3 nasa_apod.py -v -i"wallpaper" --date=20210429
```
