
def add(x: float, y: float) -> float:
    return x + y

def subtract(x: float, y: float) -> float:
    return x - y

def multiply(x: float, y: float) -> float:
    return x * y

def divide(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y

def mod(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Cannot modulo by zero.")
    return x % y

def pi() -> float:
    return 3.141592653589793

def get_x_percentage_of_y(x: float, y: float) -> float:
    return (x / 100.0) * y

def main():
    income_before_tax = 1000
    income_tax = 20
    decuction = get_x_percentage_of_y(income_tax,income_before_tax)
    net_income_after_tax = subtract(income_before_tax,decuction)

    print("before tax: ", income_before_tax)
    print("taxed amount: ", decuction)
    print("after tax:  ",net_income_after_tax)


if __name__ == "__main__":
    main()

TOOLS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "mod": mod,
    "pi": pi,
    "get_x_percentage_of_y": get_x_percentage_of_y,
}