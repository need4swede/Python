# Given a square matrix, calculate the absolute difference between the sums of its diagonals.

#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'diagonalDifference' function below.
#
# The function is expected to return an INTEGER.
# The function accepts 2D_INTEGER_ARRAY arr as parameter.
#

def diagonalDifference(arr):
    
    # Get matrix dimensions
    arr_length = len(arr)
    
    # Init counter for our loop
    count = arr_length - 1
    
    # Init our left/right diagonal sums
    l_sum, r_sum = 0, 0
    
    # Count diagonal sums
    for i in range(arr_length):
        row = arr[i]
        l_sum += row[i]
        r_sum += row[count - i]
        
    # Find difference between two sums
    total = l_sum - r_sum
    
    # Invert negative results
    if total < 0:
        total = -total
    
    # Return results
    return total

 
    
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = []

    for _ in range(n):
        arr.append(list(map(int, input().rstrip().split())))

    result = diagonalDifference(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
