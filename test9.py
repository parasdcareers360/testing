
# sample inputs
# Sample test cases for findShortestPalindrome function
# s1 = "aacecaaa"
# s2 = "abcd"
# s3 = "a"
# s4 = "racecar"
# s5 = "abc"

def findShortestPalindrome(s: str) -> str:
    def is_palindrome(text: str) -> bool:
        return text == text[::-1]

    # Find longest palindromic prefix
    for i in range(len(s), 0, -1):
        if is_palindrome(s[:i]):
            # Reverse the remaining suffix and prepend
            return s[i:][::-1] + s

    # Fallback (shouldn't be reached because single char is palindrome)
    return s[::-1] + s

print(findShortestPalindrome("aabcd"))  # dcbaabcd





s3 = "aabcd"

a = findShortestPalindrome(s3)
print(a)
# print(findShortestPalindrome(s4))  # Expected: "racecar"
# print(findShortestPalindrome(s5))  # Expected: "cbabc"
