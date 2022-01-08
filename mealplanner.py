# -*- coding: utf-8 -*-

"""
A meal planning and grocery list generator to keep #DFIRFIT
MIT License.
"""

# Imports
import os
import sys
import argparse

__author__ = 'Joshua James'
__copyright__ = 'Copyright 2022, MealPlanner'
__credits__ = []
__license__ = 'MIT'
__version__ = '0.0.1'
__maintainer__ = 'Joshua James'
__email__ = 'joshua+github@dfirscience.org'
__status__ = 'active'

def setArgs():
    parser = argparse.ArgumentParser(description=__copyright__)
    parser.add_argument('-p', '--plan', required=False, action='store_true', help='Create a full meal plan (default 7 days)')
    #parser.add_argument('-b', '--breakfast', required=False, action='store_true', help='Only generate breakfast')
    #parser.add_argument('-l', '--lunch', required=False, action='store_true', help='Only generate lunch')
    #parser.add_argument('-d', '--dinner', required=False, action='store_true', help='Only generate dinner')

    return(parser.parse_args())

def main():
    args = setArgs()
    # Read settings - meals to plan, meal times, email address
    # Configure settings
    # Authenticate with Google Calendar / Other cals?
    # Store recipes in JSON?
        # Keep meal recommendation stats?
        # Meal ranking to bias selection?
    # Add a meal
    # Mark meal as 'do not recommend' until
    # Delete a meal
    # Generate meal list
        # Specify meal type
        # Choose random meal
        # Check if recipe has a mealtime flag
        # If yes, continue, if no select again
        # Loop for X days
    # Present meal plan to user
        # Confirm meal plan
        # Add meal plan to calendar / file / email
        # Email recipe list to configured email address / file

    # Check if meal already exists on a certain day?
    # Recipe list with checkboxes

if __name__ == '__main__':
    main()