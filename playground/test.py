from typing import List

class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        """
        1. loop through the nums, k = len(nums)
        2. if nums[i] == val remove the element , append a new element _ at end of nums, k = k-1 at each iteration if successfully removed the element
        3. return k
        """
        k = len(nums)
        # for i in range(len(nums)):
        i = 0
        while i<len(nums): 
            if val==nums[i]:
                nums.pop(i)
                nums.append("_")
                k = k-1
                continue    
            i +=1
        return k
    
nums = [0,1,2,2,3,0,4,2]
val = 2

sol = Solution()

sol.removeElement(nums, val)