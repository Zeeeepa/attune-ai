"""Demo file to test progressive tier escalation."""


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def multiply_numbers(x: int, y: int) -> int:
    """Multiply two numbers.

    Args:
        x: First number
        y: Second number

    Returns:
        Product of x and y
    """
    return x * y


def calculate_area(width: float, height: float) -> float:
    """Calculate area of a rectangle.

    Args:
        width: Width of rectangle
        height: Height of rectangle

    Returns:
        Area (width * height)
    """
    if width < 0 or height < 0:
        raise ValueError("Width and height must be positive")
    return width * height
