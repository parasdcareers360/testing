# check palindrome 

def CheckPalindrome(value_: int):
    if not value_ or value_ == 0:
        return ValueError("Input is Incorrect! try again with correct input.")

    #example input = 1234
    # extracting last digit by % by 10
    temp_value_ = value_
    palindrome_value = 0
    while temp_value_>0:
        last_digit = temp_value_%10
        palindrome_value = palindrome_value*10+last_digit
        temp_value_ = temp_value_//10
    
    return value_==palindrome_value


s = CheckPalindrome(11)

print(s)