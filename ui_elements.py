from tkinter import Frame, Label, StringVar
from config import COLORS

class UIElements:
    def __init__(self, root, cart_manager):
        self.root = root
        self.cart_manager = cart_manager

        # Left Frame for Camera Feed
        self.left_frame = Frame(root, width=800, height=600)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right Frame for Cart and Info
        self.right_frame = Frame(root, width=400, height=600, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Camera Feed Label
        self.camera_label = Label(self.left_frame)
        self.camera_label.pack()

        # Cart Label
        self.cart_label = Label(self.right_frame, text="Cart", font=("Arial", 16), bg="white")
        self.cart_label.pack(pady=10)

        # Cart Items Display
        self.cart_items_var = StringVar()
        self.cart_items_label = Label(self.right_frame, textvariable=self.cart_items_var, font=("Arial", 12), bg="white")
        self.cart_items_label.pack(pady=10)

        # Total Label
        self.total_var = StringVar()
        self.total_label = Label(self.right_frame, textvariable=self.total_var, font=("Arial", 14, "bold"), bg="white")
        self.total_label.pack(pady=10)

        self.update_cart_display()

    def update_cart_display(self):
        """Update the cart display."""
        cart_text, total = self.cart_manager.get_cart_summary()
        self.cart_items_var.set(cart_text)
        self.total_var.set(f"Total: ${total:.2f}")
