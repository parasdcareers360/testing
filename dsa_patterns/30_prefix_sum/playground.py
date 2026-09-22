from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        n = len(nums)
        self.prefix = [0] * (n + 1)
        for i in range(n):
            self.prefix[i + 1] = self.prefix[i] + nums[i]

    def sumRange(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]


if __name__ == "__main__":
    num_array = NumArray([-2, 0, 3, -5, 2, -1])
    print(num_array.sumRange(0, 2))  # 1
    print(num_array.sumRange(2, 5))  # -1
    print(num_array.sumRange(0, 5))  # -3

    num_array2 = NumArray([5])
    print(num_array2.sumRange(0, 0))  # 5
    print(num_array2.sumRange(0, 0))  # 5
