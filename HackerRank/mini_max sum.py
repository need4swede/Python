# Given five positive integers, find the minimum and maximum values that can be 
# calculated by summing exactly four of the five integers. Then print the respective 
# minimum and maximum values as a single line of two space-separated long integers.

# Print two space-separated long integers denoting the respective minimum and maximum 
# values that can be calculated by summing exactly four of the five integers. 
# (The output can be greater than a 32 bit integer.)


#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'miniMaxSum' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def miniMaxSum(arr):
    
    # Get length of array
    arr_length = len(arr)
    
    # Sort in asc. order to get lowest sum
    arr_low = sorted(arr)
    arr_low_sum = 0
        
    
    # Sort in desc. order to get highest sum
    arr_high = sorted(arr, key=int, reverse=True)
    arr_high_sum = 0
    
    # Find sum of both sorted arrays
    for number in range(4):
        arr_low_sum += arr_low[number]
        arr_high_sum += arr_high[number]
    
    # Print results
    print(f"{arr_low_sum} {arr_high_sum}")
        
        

if __name__ == '__main__':

    arr = list(map(int, input().rstrip().split()))

    miniMaxSum(arr)
