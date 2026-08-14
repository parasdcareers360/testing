from typing import List

class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        """
        1. loop through the nums
        2. dict of key and value having the key = nums[i] an value as the count of the nums[i]
        3. after completing 1 loop
        4. loop through the key and values of dict and return the maximum count key
        """

        data_dict = {}
        for i in range(len(nums)):
            if nums[i] in data_dict:
                data_dict[nums[i]]+=1
                continue
            data_dict[nums[i]] = 1

        max_occurrence_digit = None
        max_count = 0
        for key in data_dict:
            if data_dict[key]>max_count:
                max_count = data_dict[key]
                max_occurrence_digit = key
        return max_occurrence_digit

nums=[3,2,3]

s = Solution()
s.majorityElement(nums)