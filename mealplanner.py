# -*- coding: utf-8 -*-

"""
A meal planning and grocery list generator to keep #DFIRFIT
MIT License.
"""

# Imports
import argparse
import logging

from json import dumps, loads
from random import choice
from wget import download
from pathlib import Path
from datetime import date, timedelta, datetime

# Calendar integration
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__software__ = 'MealPlanner'
__author__ = 'Joshua James'
__copyright__ = 'Copyright 2022, MealPlanner'
__credits__ = []
__license__ = 'MIT'
__version__ = '0.1.1'
__maintainer__ = 'Joshua James'
__email__ = 'joshua+github@dfirscience.org'
__status__ = 'active'

SCOPES = ['https://www.googleapis.com/auth/calendar']
# Set config location & name
CONFFILE = "mealplanner.conf"
RECIPELIST = "recipes.json"
CONFDIR = Path(f"{Path.home()}/.mealplanner")
CONFIG = Path(f"{CONFDIR}/{CONFFILE}")
SETTINGS = None
GROCERYLIST = {}
PLANDATE = date.today()

# Set logging level and format
def setLogging(debug):
    fmt = "[%(levelname)s] %(asctime)s %(message)s"
    LOGLEVEL = logging.INFO if debug is False else logging.DEBUG
    logging.basicConfig(level=LOGLEVEL, format=fmt, datefmt='%Y-%M-%dT%H:%M:%S')
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)

# Argparser config and argument setup
def setArgs():
    parser = argparse.ArgumentParser(description=__copyright__)
    parser.add_argument('-p', '--plan', required=False, action='store_true', help='Create a full meal plan (default 7 days)')
    parser.add_argument('--debug', required=False, action='store_true', help='Set the log level to DEBUG')
    parser.add_argument('--update', required=False, action='store_true', help='Update the recipe list.') # This will overwrite!
    parser.add_argument('-d', '--date', required=False, action='store', help='Date the plan begins (YYYY-MM-DD)')
    parser.add_argument('--googleauth', required=False, action='store_true', help='Authenticate to Google Calendar')

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
    data = {"gen_breakfast": "True", "gen_lunch": "True", "gen_dinner": "True", "duration_hr": 1, "time_breakfast": "07:00",
    "time_lunch": "12:00", "time_dinner": "18:00", "email": "test@test.null", "plan_days": 7}
    CONFIG.parent.mkdir(exist_ok=True, parents=True)
    CONFIG.write_text(dumps(data))

# Read the configuration file and store in global SETTINGS
def readConfig():
    global SETTINGS
    SETTINGS = loads(CONFIG.read_text())
    logging.debug("Settings file loaded successfully")

def downloadNewRecipes(RECIPEPATH):
    master = "https://raw.githubusercontent.com/DFIRScience/MealPlanner/main/recipes.json"
    try:
        RECIPEPATH.replace(f"{RECIPEPATH}.old") # This could lead to no recipes if download fails
        download(master, str(RECIPEPATH))
        print()
    except Exception as e:
        logging.debug(e)
        logging.info("Could not download a recipe list")
        exit(1)
    logging.debug("Recipe file downloaded successfully.")

def getRecipes():
    RECIPEPATH = Path(f"{CONFDIR}/{RECIPELIST}")
    if RECIPEPATH.exists():
        return loads(RECIPEPATH.read_text())
    else:
        logging.info(f"No recipes found at {RECIPEPATH}")
        QDOWNLOAD = input("Would you like to download recipes? (y/N) ").lower()
        if QDOWNLOAD == ("y" or "yes"): downloadNewRecipes(RECIPEPATH)
        else:
            logging.info("Please load recipes before generating a meal plan.")
            exit(1)

# Use config to determine total number of each type of meal
def getNumMealTypes(days):
    b = l = d = 0
    if SETTINGS['gen_breakfast'] == "True": b = days
    if SETTINGS['gen_lunch'] == "True": l = days
    if SETTINGS['gen_dinner'] == "True": d = days

    return b, l, d

# Randomly choose a meal and check if it matches filters
def getMeal(mealtype, recipes):
    meal, recipe = choice(list(recipes.items()))
    if recipe["meal"][mealtype] != "True":
        return getMeal(mealtype, recipes)
    else:
        return(meal)

# Get the recipe for a meal and add it to global GROCERYLIST
# Combine all of the same ingredents
def getRecipeList(recipes, meal):
    global GROCERYLIST
    ingredents = recipes[meal]["ingredients"]
    for i in ingredents:
        if i not in GROCERYLIST:
            logging.debug(f"Adding {i} to grocerylist")
            GROCERYLIST.update({i:ingredents[i]})
        else: # We already have the ingredent - add to amounts
            logging.debug(f"Updating amounts of {i}")
            for measurement in ingredents[i]:
                GROCERYLIST[i][measurement] = float(GROCERYLIST[i][measurement]) + float(ingredents[i][measurement])

# Main meal plan generator function
def getPlan():
    global PLANDATE
    recipes = getRecipes()
    logging.info(f"Generating meal plans for {SETTINGS['plan_days']} days")
    numb, numl, numd = getNumMealTypes(SETTINGS['plan_days']) # get b, l, d to filter
    logging.info(f"{numb} breakfasts, {numl} lunches, {numd} dinners")
    mealplan = {}
    for n in range(numb):
       mealplan[f'breakfast{n}'] = getMeal('breakfast', recipes)
    for n in range(numl):
       mealplan[f'lunch{n}'] = getMeal('lunch', recipes)
    for n in range(numd):
       mealplan[f'dinner{n}'] = getMeal('dinner', recipes)

    creds = authGoogleCalendar()
    calendar = getGoogleCalendar(creds)

    event = {
        'summary': '',
        'description': '',
        'start': {
            'dateTime': '',
            'timeZone': '',
        },
        'end': {
            'dateTime': '',
            'timeZone': '',
        }
    }

    for n in range(SETTINGS['plan_days']):
        td = PLANDATE + timedelta(n)
        td2 = timedelta(hours=SETTINGS['duration_hr'])
        print(f'++++ {td.strftime("%Y-%m-%d")} Mealplan ++++')
        if numb != 0:
            b = mealplan[f'breakfast{n}']
            event['summary'] = b
            event['description'] = recipes[mealplan[f'breakfast{n}']]["recipe"]
            event['start']['dateTime'] = td.strftime("%Y-%m-%d") + "T" + SETTINGS['time_breakfast'] + ":00"
            event['start']['timeZone'] = calendar['timeZone']
            event['end']['dateTime'] = (datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S') + td2).isoformat()
            event['end']['timeZone'] = calendar['timeZone']
            logging.debug(event)
            print(b)
            if creds.valid: addToGoogleCalendar(creds, calendar, event)
            getRecipeList(recipes, mealplan[f'breakfast{n}'])
        if numl != 0:
            l = mealplan[f'lunch{n}']
            event['summary'] = l
            event['description'] = recipes[mealplan[f'lunch{n}']]["recipe"]
            event['start']['dateTime'] = td.strftime("%Y-%m-%d") + "T" + SETTINGS['time_lunch'] + ":00"
            event['start']['timeZone'] = calendar['timeZone']
            event['end']['dateTime'] = (datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S') + td2).isoformat()
            event['end']['timeZone'] = calendar['timeZone']
            logging.debug(event)
            print(l)
            if creds.valid: addToGoogleCalendar(creds, calendar, event)
            getRecipeList(recipes, mealplan[f'lunch{n}'])
        if numd != 0:
            d = mealplan[f'dinner{n}']
            print(d)
            event['summary'] = d
            event['description'] = recipes[mealplan[f'dinner{n}']]["recipe"]
            event['start']['dateTime'] = td.strftime("%Y-%m-%d") + "T" + SETTINGS['time_dinner'] + ":00"
            event['start']['timeZone'] = calendar['timeZone']
            event['end']['dateTime'] = (datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S') + td2).isoformat()
            event['end']['timeZone'] = calendar['timeZone']
            logging.debug(event)
            if creds.valid: addToGoogleCalendar(creds, calendar, event)
            getRecipeList(recipes, mealplan[f'dinner{n}'])

def getGroceryList():
    print("")
    print("======== Grocery List ========")
    for item in GROCERYLIST:
        for measurement in GROCERYLIST[item]:
            print(f"{item.capitalize()}: {GROCERYLIST[item][measurement]} {measurement}")

def authGoogleCalendar():
    global SCOPES
    creds = None
    TOKENPATH = Path(f"{CONFDIR}/caltoken.json")
    CREDSPATH = Path(f"{CONFDIR}/credentials.json")
    if TOKENPATH.exists():
        creds = Credentials.from_authorized_user_file(TOKENPATH, SCOPES)
        logging.debug("Prior Google auth token found")
    if not creds or not creds.valid:
        logging.debug("Credentials expired. Refreshing...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDSPATH, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKENPATH.write_text(creds.to_json())
    return creds

def getGoogleCalendar(creds):
    logging.debug("Getting meal plan calendar ID")
    calID = None
    try:
        service = build('calendar', 'v3', credentials=creds)
        pageToken = None
        # Get the Meal Plan calendar ID - TODO - create if not found
        while True:
            calendarList = service.calendarList().list(pageToken=pageToken).execute()
            for calendarListEntry in calendarList['items']:
                if calendarListEntry["summary"] == "Meal Plan":
                    calID = calendarListEntry["id"]
                    break
            page_token = calendarList.get('nextPageToken')
            if not page_token:
               break
        calendar = service.calendars().get(calendarId=calID).execute()
        return calendar

    except HttpError as error:
        logging.debug(f'An error occurred: {error}')

def addToGoogleCalendar(creds, calendar, event):
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId=calendar['id'], body=event).execute()
    except HttpError as error:
        logging.debug(f'An error occurred: {error}')

def main():
    global PLANDATE
    args = setArgs()
    setLogging(args.debug)
    print(f"{__software__} v{__version__}")
    if args.googleauth: authGoogleCalendar()
    if args.update:
        logging.info("Updating recipes")
        downloadNewRecipes(Path(f"{CONFDIR}/{RECIPELIST}"))
        exit()
    settingsInit()
    if args.date: PLANDATE = datetime.strptime(args.date, '%Y-%m-%d')
    logging.debug(f'Plan start date set to {PLANDATE}')
    if args.plan:
        getPlan()
        getGroceryList()

if __name__ == '__main__':
    main()