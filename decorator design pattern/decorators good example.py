from abc import ABC, abstractmethod

class Coffee(ABC):

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

# every coffee object needs to implement these methods.

class SimpleCoffee(Coffee):

    def get_price(self):
        return 5

    def get_description(self):
        return "simple coffee"

# base decorator

class CoffeeDecorator(Coffee):

    def __init__(self, coffee: Coffee):
        self.coffee = coffee

# a decorator design pattern needs to have IS-A relationship and HAS-A relationship
# inheritance -- inheriting the class
# composition -- containing the object of the class

