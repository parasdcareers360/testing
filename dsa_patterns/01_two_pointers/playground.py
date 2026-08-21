# brute force with n^2 approach

# def twoSum(nums: list, target: int):
#     for i in range(len(nums)-1):
#         for j in range(i+1,len(nums)):
#             if nums[i]+nums[j]==target:
#                 return [i, j]

    # return []

# def twoSum(nums: list, target: int):is_anonymous_case
#     left = 0
#     right = len(nums)-1

#     while left<right:
#         sum = nums[left]+nums[right]
#         if sum==target:
#             return [left, right]

#         if sum>target:
#             right-=1
#         else:
#             left+=1
#     return []

# example input


# nums = [-1,-2,3]

# i = 0 , # ie. -1
# j = 1 , # i.e -2
# k = 2 , # i.e  3
# nums[i]+nums[j]+nums[k]

# -1+(-2)+3 = 0

# answer = [[-1,-2,3]]


def threeSumBruteForce(nums):
    n = len(nums)
    result = []

    # Iterate over all possible triplets (i, j, k) with i < j < k
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    result.append([nums[i], nums[j], nums[k]])

    # Remove duplicate triplets
    result = [list(x) for x in set(tuple(x) for x in result)]

    return result


input = [-1, 0, 1, 2, -1, -4]
expected = [[-1, -1, 2], [-1, 0, 1]]

getting = [[0, 1, -1], [-1, 0, 1], [-1, 2, -1]]

a = threeSumBruteForce(input)
print(a)










# numbers = [2, 7, 11, 15]
# target = 9


# a = twoSum(numbers, target)

# print(a)