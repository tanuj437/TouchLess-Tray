class CartManager:
    def __init__(self, menu):
        self.menu = menu
        self.cart = {}

    def add_item(self, item):
        """Add an item to the cart."""
        if item in self.cart:
            self.cart[item] += 1
        else:
            self.cart[item] = 1

    def remove_item(self, item):
        """Remove an item from the cart."""
        if item in self.cart:
            if self.cart[item] > 1:
                self.cart[item] -= 1
            else:
                del self.cart[item]

    def get_cart_summary(self):
        """Return cart items and total price."""
        cart_text = ""
        total = 0
        for item, quantity in self.cart.items():
            price = self.menu.get(item, 0) * quantity
            total += price
            cart_text += f"{item} x{quantity}: ${price:.2f}\n"
        return cart_text, total

    def process_gesture(self, index_finger_pos):
        """Processes gestures based on index finger position."""
        if index_finger_pos:
            x, y = index_finger_pos
            if 100 < x < 200 and 100 < y < 200:
                self.add_item("Burger")
                print("Added Burger to cart")
            elif 200 < x < 300 and 100 < y < 200:
                self.add_item("Pizza")
                print("Added Pizza to cart")
            elif 100 < x < 200 and 200 < y < 300:
                self.remove_item("Burger")
                print("Removed Burger from cart")
            elif 200 < x < 300 and 200 < y < 300:
                self.remove_item("Pizza")
                print("Removed Pizza from cart")
