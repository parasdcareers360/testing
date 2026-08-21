# two sum with dict

# input = [1,2,3]
# target = 3

def TwoSum(nums: list, target: int):
    seen = {}

    for i in range(len(nums)):
        if target-nums[i] in seen: # 3-1 =2 , 3-2 = 1 
            return [seen[target-nums[i]], i]
        seen[nums[i]] = i # seen = {1:0, 2:1}


print(TwoSum([1,2,3], 5))
