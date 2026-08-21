# two sum

# numbers = [2, 7, 11, 15], target = 9 Output: [1, 2]

'''
1. brute force -- using two loops i from 0 to (n-1) and j from i+1 to n where n = len(nums) summing both nums[i] and nums[j] if equals to target then return 

2. using sliding window -- using left pointer at 0th index and right at nth index squizing right and left if target - sum(nums[left],nums[right])!=0 and if sum>target then right to left and if not then left to right

3. using dict -- with for loop from 0 to n -- if target - nums[i] in dict.keys() return [dict[nums[i]], i] else dict[nums[i]]=i

'''