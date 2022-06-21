# Given an array of integers, calculate the ratios of its elements 
# that are positive, negative, and zero. Print the decimal value of 
# each fraction on a new line with 6 places after the decimal.

#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'plusMinus' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def plusMinus(arr):
    # Number of elements
    arr_length = len(arr)
    
    # Value Sums
    positives, negatives, zeroes = 0, 0, 0
    
    # Iterate through array
    for number in range(arr_length):
        if arr[number] > 0:
            positives += 1
        elif arr[number] == 0:
            zeroes += 1
        else:
            negatives += 1
    
    # Get averages
    positives = positives / arr_length
    negatives = negatives / arr_length
    zeroes = zeroes / arr_length
    
    # Print to console
    print(f"{positives:.6f}")
    print(f"{negatives:.6f}")
    print(f"{zeroes:.6f}")
        
        
if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    plusMinus(arr)
