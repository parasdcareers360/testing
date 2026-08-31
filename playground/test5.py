from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """
        1. loop through the nums 0 to len(nums)-1 -- pointer i
        2. loop through the nums i+1 to len(nums) -- pointer j
        3. if nums[i]+nums[j] == target return [i,j]
        """

        # for i in range(len(nums)-1):
        #     for j in range(i+1,len(nums)):
        #         if nums[i]+nums[j]==target:
        #             return [i,j]

        seen = {}
        for i in range(len(nums)):
            needed = target - nums[i]

            if needed in seen:
                return [seen[needed],i]
            seen[nums[i]]=i
        
                 


s = Solution()
nums = [2,11,7,15]
target = 9

data=s.twoSum(nums, target)
print(data)