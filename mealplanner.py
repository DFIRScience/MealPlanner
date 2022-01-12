# -*- coding: utf-8 -*-

"""
A meal planning and grocery list generator to keep #DFIRFIT
MIT License.
"""

# Imports
import os
import sys
import argparse
import logging
import json
import base64
import requests

from pathlib import Path

__software__ = 'MealPlanner'
__author__ = 'Joshua James'
__copyright__ = 'Copyright 2022, MealPlanner'
__credits__ = []
__license__ = 'MIT'
__version__ = '0.0.2'
__maintainer__ = 'Joshua James'
__email__ = 'joshua+github@dfirscience.org'
__status__ = 'active'

# Set config location & name
CONFFILE = "mealplanner.conf"
RECIPELIST = "recipes.json"
CONFDIR = Path(f"{Path.home()}/.mealplanner")
CONFIG = Path(f"{CONFDIR}/{CONFFILE}")
SETTINGS = None

# Set logging level and format
def setLogging(debug):
    fmt = "[%(levelname)s] %(asctime)s %(message)s"
    LOGLEVEL = logging.INFO if debug is False else logging.DEBUG
    logging.basicConfig(level=LOGLEVEL, format=fmt, datefmt='%Y-%M-%dT%H:%M:%S')

# Argparser config and argument setup
def setArgs():
    parser = argparse.ArgumentParser(description=__copyright__)
    parser.add_argument('-p', '--plan', required=False, action='store_true', help='Create a full meal plan (default 7 days)')
    parser.add_argument('--debug', required=False, action='store_true', help='Set the log level to DEBUG')
    #parser.add_argument('-b', '--breakfast', required=False, action='store_true', help='Only generate breakfast')
    #parser.add_argument('-l', '--lunch', required=False, action='store_true', help='Only generate lunch')
    #parser.add_argument('-d', '--dinner', required=False, action='store_true', help='Only generate dinner')

    return(parser.parse_args())

# Check for settings config file - load if found, create if not found.
def settingsInit():
    if not CONFIG.exists():
        logging.debug("Config file not found!")
        createConfig()
        settingsInit()
    else:
        logging.debug("Config file found!")
        readConfig()

# Create a default config file
def createConfig():
    logging.info("Creating new config file...")
    logging.debug(f"Config directory set to {CONFIG}")
    data = {"gen_breakfast": True, "gen_lunch": True, "gen_dinner": True, "duration_hr": 1, "time_breakfast": "07:00",
    "time_lunch": "12:00", "time_dinner": "18:00", "email": "test@test.null", "plan_days": 7}
    CONFIG.parent.mkdir(exist_ok=True, parents=True)
    CONFIG.write_text(json.dumps(data))

# Read the configuration file and store in global SETTINGS
def readConfig():
    global SETTINGS
    SETTINGS = json.loads(CONFIG.read_text())
    logging.debug("Settings file loaded successfully")

def downloadNewRecipes(RECIPEPATH):
    master = "https://raw.githubusercontent.com/DFIRScience/MealPlanner/main/recipes.json"
    try:
        req = requests.get(master)
    except Exception as e:
        logging.debug(e)
        logging.info("Could not download a recipe list")
        exit(1)
    RECIPEPATH.write_text(json.dumps(req.text))

def getRecipes():
    RECIPEPATH = Path(f"{CONFDIR}/{RECIPELIST}")
    if RECIPEPATH.exists():
        return RECIPEPATH.read_text()
    else:
        logging.info(f"No recipes found at {RECIPEPATH}")
        QDOWNLOAD = input("Would you like to download recipes? (y/N) ").lower()
        if QDOWNLOAD == ("y" or "yes"): downloadNewRecipes(RECIPEPATH)
        else: logging.info("Please load recipes before generating a meal plan.")

def getPlan():
    recipies = getRecipes()
    logging.info(f"Generating meal plans for {SETTINGS['plan_days']} days")
    

def main():
    args = setArgs()
    setLogging(args.debug)
    print(f"{__software__} v{__version__}")
    settingsInit()
    if args.plan: getPlan()

if __name__ == '__main__':
    main()