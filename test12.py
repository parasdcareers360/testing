# print factors / divisors

# input = 10
# op = [1, 2, 5, 10]

# def getDivisors(number: int):
#     if not number or number ==0:
#         raise ValueError("Error wrong input!")

#     divisors = []
#     for i in range(1,number+1):
#         if number%i==0:
#             divisors.append(i)

    # return divisors

# def getDivisors(number: int):
#     if not number or number ==0:
#         raise ValueError("Error wrong Input!")

#     divisors = []
#     half = number//2
#     for i in range(1, half):
#         if number%i==0:
#             divisors.append(i)
#             if number/i not in divisors:
#                 divisors.append(number//i)
#     return divisors

def getDivisors(number: int):
    if not number or number ==0:
        raise ValueError("Error wrong Input!")

    import math

    sqrt_number = int(math.sqrt(number))
    result = []
    divisor = []
    for i in range(1, sqrt_number+1):
        if number%i==0:
            divisor.append(i)
            if number//i not in divisor:
                divisor.append(number//i)
    return divisor


print(getDivisors(36))
