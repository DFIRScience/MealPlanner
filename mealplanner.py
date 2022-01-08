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


if __name__ == '__main__':
    main()