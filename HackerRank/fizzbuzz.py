#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'fizzBuzz' function below.
#
# The function accepts INTEGER n as parameter.
#

def fizzBuzz(n):
    
    # Loop arguments
    start, end = 1, n+1
    
    # Phrases
    div3, div5, div3and5 = 'Fizz', 'Buzz', 'FizzBuzz'
    
    # Loop through array
    for number in range(start, end):
        
        # Divisible by 3 and 5
        if number % 3 == 0 and number % 5 == 0:
            print(div3and5)

        # Divisible by 3
        elif number % 3 == 0:
            print(div3)

        # Divisible by 5
        elif number % 5 == 0:
            print(div5)
        
        # Not divisible by 3 or 5
        else:
            print(number)

if __name__ == '__main__':
    n = int(input().strip())

    fizzBuzz(n)
