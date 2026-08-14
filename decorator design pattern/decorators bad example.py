# decorators are used to add new functionality to objects dynamically without changing its originial code.


# 1. design pattern decorator (oops design patteran comes under structural design pattern)
# 2. python @decorator syntax (function / class decorator)


# coffee
class Coffee():
    # price
    def get_price(self):
        return 5

    # description
    def get_description(self):
        return "simple coffee"

class MilkCoffee(Coffee):
    # price
    def get_price(self):
        return 8

    # description
    def get_description(self):
        return "simple coffee + milk"


class SugarCoffee(Coffee):
    # price
    def get_price(self):
        return 6

    # description
    def get_description(self):
        return "simple coffee + sugar"


class ChocolateCoffee(Coffee):
    # price
    def get_price(self):
        return 10

    # description
    def get_description(self):
        return "simple coffee + sugar + chocolate"


class MilkSugarChocolateCoffee(Coffee):
    # price
    def get_price(self):
        return 12

    # description
    def get_description(self):
        return "simple coffee + milk + sugar + chocolate"

# suppose we have to add flavour into the coffee then we need to add as many classes as our flavours. this problem is called as class explosion.

