#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'countingSort' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def create_frequency(length):
    freq_arr = []
    for i in range(length):
        freq_arr.append(0)
    return freq_arr
        

def countingSort(arr):
    
    # Get length of array
    arr_length = len(arr) + 1
    
    # Create a new array with zeroes (101 for looping 0 indexing)
    freq_arr = create_frequency(101)
    
    # Add integers to frequency array
    for i in range(arr_length):
        
        try:
            # Get the number in the original array
            arr_num = arr[i]
            
            # If we reached the end of the array...
        except IndexError:
            # Remove our additional element, and break loop
            freq_arr.pop()
            break
        
        # Find the number in our frequency array,
        # using arr_num as our index
        freq_num = freq_arr[arr_num] # 0
        
        # Count +1 to the freqency array @ index array_num
        updated_freq_num = freq_num + 1 # 1
        
        # Replace the old number with the new one
        freq_arr[arr_num] = updated_freq_num # 1
    
    # Return array
    return freq_arr

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = countingSort(arr)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
