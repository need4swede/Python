# Given a time in -hour AM/PM format, convert it to military (24-hour) time.

# Complete the timeConversion function in the editor below. It should return a new string representing the input time in 24 hour format.

#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'timeConversion' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

def timeConversion(s):
    
    # Split time into sections
    hours = str(s.split(':')[0])
    minutes = str(s.split(':')[1])
    seconds = str(s.split(':')[2])[0:2]
    am_pm = str(s.split(':')[2])[2:4]
    
    # Check PM
    if am_pm.lower() == 'pm':
        
        # Add hours
        digital_hours = 12 + int(hours)
        
        # Convert 24 to 12
        if digital_hours == 24:
            digital_hours = 12
    
    # Check AM
    elif am_pm.lower() == 'am':
        
        # Add hours
        digital_hours = hours
        
        # Convert 12 to 00
        if digital_hours == '12':
            digital_hours = '00'
    else:
        return 'Invalid Time Format'
    
    # Construct digital time
    digital_time = f"{digital_hours}:{minutes}:{seconds}"
    
    # Return time
    return digital_time
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = timeConversion(s)

    fptr.write(result + '\n')

    fptr.close()
