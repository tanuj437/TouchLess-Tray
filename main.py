import cv2
import mediapipe as mp
import numpy as np
import time
import json
from tkinter import Tk, Label, Frame, Button, StringVar
from PIL import Image, ImageTk

class TouchlessOrdering:
    def __init__(self, root):
        self.root = root
        self.root.title("Touchless Ordering System")
        self.root.geometry("1200x600")

        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera. Please check your camera connection.")

        # Load menu from JSON file
        self.menu = self.load_menu("menu.json")
        self.cart = {}

        # Screen states
        self.SCREENS = {
            'HOME': 'home_screen',
            'ADD_ITEMS': 'add_items_screen',
            'VIEW_CART': 'view_cart_screen',
            'CHECKOUT': 'checkout_screen',
            'CONFIRM_DELETE': 'confirm_delete_screen'
        }
        self.current_screen = self.SCREENS['HOME']

        # UI Elements
        self.home_buttons = {
            "Add Items": [50, 100, 350, 170],
            "View Cart": [50, 200, 350, 270],
            "Quit": [50, 300, 350, 370]
        }

        self.add_items_buttons = {}
        self.view_cart_buttons = {}
        self.confirm_delete_buttons = {
            "Yes": [50, 300, 200, 370],
            "No": [250, 300, 400, 370]
        }

        # Selection cooldown
        self.selection_cooldown = 1.0  # Seconds
        self.last_selection_time = 0

        # Item to be deleted (for confirmation dialog)
        self.item_to_delete = None

        # Color scheme
        self.COLORS = {
            'PRIMARY': (46, 204, 113),  # Green
            'SECONDARY': (52, 152, 219),  # Blue
            'ACCENT': (231, 76, 60),  # Red
            'BACKGROUND': (44, 62, 80),  # Dark Blue
            'TEXT': (236, 240, 241),  # White
            'HOVER': (39, 174, 96)  # Darker Green
        }

        # Tkinter GUI Setup
        self.setup_gui()

    def setup_gui(self):
        """Set up the Tkinter GUI."""
        # Left Frame for Camera Feed
        self.left_frame = Frame(self.root, width=800, height=600)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right Frame for Cart and Info
        self.right_frame = Frame(self.root, width=400, height=600, bg="white")
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

        # Update Cart Display
        self.update_cart_display()

    def update_cart_display(self):
        """Update the cart display in the Tkinter GUI."""
        cart_text = ""
        total = 0
        for item, quantity in self.cart.items():
            price = self.menu[item] * quantity
            total += price
            cart_text += f"{item} x{quantity}: ${price:.2f}\n"
        self.cart_items_var.set(cart_text)
        self.total_var.set(f"Total: ${total:.2f}")

    def load_menu(self, filename):
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

    def check_collision(self, point, rect):
        """Check if a point is within a rectangle."""
        if point is None:
            return False
        x, y = point
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2

    def draw_fancy_button(self, frame, text, coords, is_hover=False, color=None):
        """Draw a modern-looking button with animations."""
        if color is None:
            color = self.COLORS['PRIMARY']

        # Create button shadow
        shadow_offset = 5
        shadow_coords = [x + shadow_offset for x in coords]
        cv2.rectangle(frame, (shadow_coords[0], shadow_coords[1]),
                      (shadow_coords[2], shadow_coords[3]),
                      (0, 0, 0), -1)

        # Create main button
        button_color = self.COLORS['HOVER'] if is_hover else color
        cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]),
                      button_color, cv2.FILLED)

        # Add button border
        cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]),
                      self.COLORS['TEXT'], 2)

        # Add text with shadow
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = coords[0] + (coords[2] - coords[0] - text_size[0]) // 2
        text_y = coords[1] + (coords[3] - coords[1] + text_size[1]) // 2

        # Draw text shadow
        cv2.putText(frame, text, (text_x + 2, text_y + 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Draw main text
        cv2.putText(frame, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)

    def draw_home_screen(self, frame, index_finger_pos):
        """Draw the home screen."""
        self.draw_header(frame, "Home Screen")
        for text, coords in self.home_buttons.items():
            is_hover = self.check_collision(index_finger_pos, coords)
            self.draw_fancy_button(frame, text, coords, is_hover)

    def draw_add_items_screen(self, frame, index_finger_pos):
        """Draw the add items screen."""
        self.draw_header(frame, "Add Items")
        y_offset = 100
        self.add_items_buttons.clear()

        for item, price in self.menu.items():
            display_text = f"{item}: ${price:.2f}"
            cv2.putText(frame, display_text, (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)

            # Add + button
            add_button_coords = [300, y_offset - 25, 350, y_offset + 5]
            self.add_items_buttons[f"add_{item}"] = add_button_coords
            is_hover = self.check_collision(index_finger_pos, add_button_coords)
            self.draw_fancy_button(frame, "+", add_button_coords, is_hover, self.COLORS['SECONDARY'])

            # Display current quantity in cart
            quantity = self.cart.get(item, 0)
            cv2.putText(frame, f"x{quantity}", (370, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)

            # Add - button
            reduce_button_coords = [400, y_offset - 25, 450, y_offset + 5]
            self.add_items_buttons[f"reduce_{item}"] = reduce_button_coords
            is_hover = self.check_collision(index_finger_pos, reduce_button_coords)
            self.draw_fancy_button(frame, "-", reduce_button_coords, is_hover, self.COLORS['ACCENT'])

            y_offset += 50

        # Back to Home button
        back_button_coords = [50, y_offset, 350, y_offset + 70]
        self.add_items_buttons["back_to_home"] = back_button_coords
        is_hover = self.check_collision(index_finger_pos, back_button_coords)
        self.draw_fancy_button(frame, "Back to Home", back_button_coords, is_hover, self.COLORS['ACCENT'])

    def draw_view_cart_screen(self, frame, index_finger_pos, finger_count):
        """Draw the view cart screen."""
        self.draw_header(frame, "View Cart")
        y_offset = 100
        self.view_cart_buttons.clear()

        if self.cart:
            for item, quantity in self.cart.items():
                price = self.menu[item] * quantity
                text = f"{item} x{quantity}: ${price:.2f}"
                cv2.putText(frame, text, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)

                delete_coords = [350, y_offset - 25, 400, y_offset + 5]
                self.view_cart_buttons[f"delete_{item}"] = delete_coords
                is_hover = self.check_collision(index_finger_pos, delete_coords)

                if is_hover and finger_count == 1:
                    self.item_to_delete = item
                    self.current_screen = self.SCREENS['CONFIRM_DELETE']
                    return

                self.draw_fancy_button(frame, "X", delete_coords, is_hover, self.COLORS['ACCENT'])
                y_offset += 50

            checkout_coords = [50, y_offset, 350, y_offset + 70]
            self.view_cart_buttons["checkout"] = checkout_coords
            is_hover = self.check_collision(index_finger_pos, checkout_coords)
            self.draw_fancy_button(frame, "Checkout", checkout_coords, is_hover, self.COLORS['SECONDARY'])

            back_button_coords = [50, frame.shape[0] - 100, 350, frame.shape[0] - 30]
            self.view_cart_buttons["back_to_home"] = back_button_coords
            is_hover = self.check_collision(index_finger_pos, back_button_coords)
            self.draw_fancy_button(frame, "Back to Home", back_button_coords, is_hover, self.COLORS['ACCENT'])

        else:
            cv2.putText(frame, "Your cart is empty!", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, self.COLORS['TEXT'], 2)

    def draw_confirm_delete_screen(self, frame, index_finger_pos):
        """Draw the confirm delete screen and handle deletion."""
        self.draw_header(frame, "Confirm Delete")
        
        if self.item_to_delete:
            # Display the confirmation message
            cv2.putText(frame, f"Delete {self.item_to_delete}?", (50, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, self.COLORS['TEXT'], 2)

            # Draw the "Yes" and "No" buttons
            for text, coords in self.confirm_delete_buttons.items():
                is_hover = self.check_collision(index_finger_pos, coords)
                self.draw_fancy_button(frame, text, coords, is_hover)

                # Handle button clicks
                if is_hover:
                    if text == "Yes":
                        # Delete the item from the cart
                        if self.item_to_delete in self.cart:
                            del self.cart[self.item_to_delete]
                            print(f"Deleted {self.item_to_delete} from the cart.")
                        self.current_screen = self.SCREENS['VIEW_CART']
                        self.item_to_delete = None  # Reset the item to delete
                    elif text == "No":
                        # Cancel deletion and return to the cart screen
                        self.current_screen = self.SCREENS['VIEW_CART']
                        self.item_to_delete = None  # Reset the item to delete
        else:
            # If no item is selected for deletion, return to the cart screen
            self.current_screen = self.SCREENS['VIEW_CART']
            self.item_to_delete = None

    def draw_checkout_screen(self, frame):
        """Draw the checkout screen and handle the transition back to the home screen."""
        self.draw_header(frame, "Order Placed!")
        total = 0
        y_offset = 200

        # Display order items and calculate total
        for item, quantity in self.cart.items():
            price = self.menu[item] * quantity
            total += price
            order_text = f"{item} x{quantity}: ${price:.2f}"
            cv2.putText(frame, order_text, (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)
            y_offset += 30

        # Display total
        cv2.putText(frame, f"Total: ${total:.2f}", (50, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLORS['TEXT'], 2)

        # Track the time when the checkout screen is first displayed
        if not hasattr(self, 'checkout_start_time'):
            self.checkout_start_time = time.time()

        # Transition back to the home screen after 5 seconds
        if time.time() - self.checkout_start_time >= 5:
            self.cart.clear()  # Clear the cart
            self.current_screen = self.SCREENS['HOME']  # Return to the home screen
            del self.checkout_start_time  # Reset the timer

    def draw_header(self, frame, text):
        """Draw a fancy header."""
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 70),
                      self.COLORS['SECONDARY'], cv2.FILLED)
        cv2.putText(frame, text, (50, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, self.COLORS['TEXT'], 2)

    def handle_selection(self, finger_count, index_finger_pos):
        """Handle selection based on finger count."""
        current_time = time.time()
        if current_time - self.last_selection_time < self.selection_cooldown:
            return

        if self.current_screen == self.SCREENS['HOME']:
            for text, coords in self.home_buttons.items():
                if self.check_collision(index_finger_pos, coords):
                    if text == "Add Items":
                        self.current_screen = self.SCREENS['ADD_ITEMS']
                    elif text == "View Cart":
                        self.current_screen = self.SCREENS['VIEW_CART']
                    elif text == "Quit":
                        self.cap.release()
                        cv2.destroyAllWindows()
                        self.root.quit()
                    self.last_selection_time = current_time
                    break

        elif self.current_screen == self.SCREENS['ADD_ITEMS']:
            for button_id, coords in self.add_items_buttons.items():
                if self.check_collision(index_finger_pos, coords):
                    if button_id.startswith("add_"):
                        item = button_id[4:]
                        self.cart[item] = self.cart.get(item, 0) + 1
                        self.update_cart_display()
                    elif button_id.startswith("reduce_"):
                        item = button_id[7:]
                        if item in self.cart:
                            if self.cart[item] > 1:
                                self.cart[item] -= 1
                            else:
                                del self.cart[item]
                            self.update_cart_display()
                    elif button_id == "back_to_home":
                        self.current_screen = self.SCREENS['HOME']
                    self.last_selection_time = current_time
                    break

        elif self.current_screen == self.SCREENS['VIEW_CART']:
            for button_id, coords in self.view_cart_buttons.items():
                if button_id.startswith("delete_"):
                    if self.check_collision(index_finger_pos, coords):
                        self.item_to_delete = button_id[7:]
                        self.current_screen = self.SCREENS['CONFIRM_DELETE']
                        self.last_selection_time = current_time
                        return


            if self.check_collision(index_finger_pos, self.view_cart_buttons.get("checkout", [-1, -1, -1, -1])):
                self.current_screen = self.SCREENS['CHECKOUT']
                self.last_selection_time = current_time
            elif self.check_collision(index_finger_pos, self.view_cart_buttons.get("back_to_home", [-1, -1, -1, -1])):
                self.current_screen = self.SCREENS['HOME']
                self.last_selection_time = current_time

        elif self.current_screen == self.SCREENS['CONFIRM_DELETE']:
            if finger_count == 2:
                for text, coords in self.confirm_delete_buttons.items():
                    if self.check_collision(index_finger_pos, coords):
                        if text == "Yes":
                            if self.item_to_delete in self.cart:
                                del self.cart[self.item_to_delete]
                                self.update_cart_display()
                        elif text == "No":
                            pass
                        self.current_screen = self.SCREENS['VIEW_CART']
                        self.item_to_delete = None
                        self.last_selection_time = current_time
                        return

    def update_frame(self):
        """Update the camera feed and handle selections."""
        success, frame = self.cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        index_finger_pos = None
        finger_count = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                index_finger_pos = (int(hand_landmarks.landmark[8].x * frame.shape[1]),
                                   int(hand_landmarks.landmark[8].y * frame.shape[0]))
                finger_count = len(results.multi_hand_landmarks)

                # Handle selection
                self.handle_selection(finger_count, index_finger_pos)

        # Draw the current screen
        if self.current_screen == self.SCREENS['HOME']:
            self.draw_home_screen(frame, index_finger_pos)
        elif self.current_screen == self.SCREENS['ADD_ITEMS']:
            self.draw_add_items_screen(frame, index_finger_pos)
        elif self.current_screen == self.SCREENS['VIEW_CART']:
            self.draw_view_cart_screen(frame, index_finger_pos, finger_count)
        elif self.current_screen == self.SCREENS['CHECKOUT']:
            self.draw_checkout_screen(frame)
        elif self.current_screen == self.SCREENS['CONFIRM_DELETE']:
            self.draw_confirm_delete_screen(frame, index_finger_pos)

        # Convert the frame to a format Tkinter can display
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)

        # Schedule the next frame update
        self.root.after(10, self.update_frame)

    def run(self):
        """Start the application."""
        self.update_frame()
        self.root.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = TouchlessOrdering(root)
    app.run()