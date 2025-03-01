import json

def load_menu(filename):
    """Load menu items from a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Menu file '{filename}' not found. Using default menu.")
        return {
            "Burger": 2.01,
            "Pizza": 5.00,
            "Pasta": 4.50,
            "Fries": 1.50,
            "Soda": 1.00,
            "Coffee": 2.00
        }

