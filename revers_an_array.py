

input = [1,2,3,4]

op = [4,3,2,1]

def reverseAnArray(nums: list):

    if not nums:
        raise ValueError("Wrong Input!")

    result = []

    for i in range(len(nums)-1,-1, -1):
        result.append(nums[i])

    return result


print(reverseAnArray(input))
