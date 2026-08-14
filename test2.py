
# Base Component
class Beverage:
    def get_description(self):
        return "Unknown beverage"

    def cost(self):
        return 0.0

# Concrete Component
class Espresso(Beverage):
    def __init__(self):
        self.description = "Espresso"

    def cost(self):
        return 1.99

# Decorator
class CondimentDecorator(Beverage):
    def __init__(self, beverage):
        self.beverage = beverage

    def get_description(self):
        return self.beverage.get_description()

# Concrete Decorators
class Milk(CondimentDecorator):
    def __init__(self, beverage):
        super().__init__(beverage)

    def get_description(self):
        return f"{self.beverage.get_description()}, Milk"

    def cost(self):
        return self.beverage.cost() + 0.50

class Soy(CondimentDecorator):
    def __init__(self, beverage):
        super().__init__(beverage)

    def get_description(self):
        return f"{self.beverage.get_description()}, Soy"

    def cost(self):
        return self.beverage.cost() + 0.30

# Usage
espresso = Espresso()
print(f"{espresso.get_description()} - ${espresso.cost()}")

milk_espresso = Milk(espresso)
print(f"{milk_espresso.get_description()} - ${milk_espresso.cost()}")

soy_milk_espresso = Soy(milk_espresso)
