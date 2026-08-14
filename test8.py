def factorial(n):
    if n==1:
        return  1
    return n*(factorial(n-1))

# print(factorial(5))


def solution(n: int, p: int):
    """
    find n! 
    return n!//p
    """
    factorial_result = factorial(n)
    return factorial_result%p

print(solution(4,5))

    