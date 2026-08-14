
def sample_decorator(func):
    def wrapper():
        print("Starting the function...")
        func()
        print("Ending the funciton...")
    return wrapper


@sample_decorator
def test_fun():
    print("Testing the function execution...")


test_fun()
