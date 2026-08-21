a = [2, 1, 5, 1, 3, 2]
k = 3

# op = 9

def maximumSubArray(nums: list, k: int):
    if len(nums)==0:
        raise ValueError("Wrong Input! length of array cannot be zero.")

    if k>len(nums):
        raise ValueError("Wrong Input! Value of k cannot be more then length of array.")
    

    left = 0
    right = k-1
    max_value = 0
    while right<len(nums):
        value = sum(nums[left:right+1])
        if value>max_value:
            max_value = value
        left+=1
        right+=1

    return max_value

a = maximumSubArray(a, k)

print(a)