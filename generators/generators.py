def sum(nums: list):
    for i in nums:
        yield i


# generator object
# print(sum(nums=[1,2,3]))

data = sum([1,2,3])


print(next(data))

print(next(data))

print(next(data))