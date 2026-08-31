from typing import List

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        '''
        1. loop through the nums , k = len(nums)
        2. existing_values : list = [] for checking the duplicates
        3. if nums[i] in existing_values 
        4. then nums.pop(i) nums.append("_"), k -=1
        '''
        i=0
        k = len(nums)
        existing_values = []
        while i<len(nums):
            if nums[i] in existing_values and nums[i]!="_":
                nums.pop(i)
                nums.append("_")
                k-=1
                continue
            existing_values.append(nums[i])
            i+=1
        return k

nums = [1,1,2]

s = Solution()

s.removeDuplicates(nums)