import tkinter as tk
import pydirectinput
import ctypes

def display_position():
    """
    Displays the current mouse position in a small window that follows the mouse cursor.
    The window appears near the mouse, slightly above and to the right.
    """
    root = tk.Tk()
    root.title("Mouse Position")
    root.geometry("200x50")
    root.attributes("-topmost", True)
    root.overrideredirect(True)  # Remove window borders
    root.attributes("-alpha", 0.8)

    # Set DPI awareness for accurate mouse position on high-DPI displays
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        pass

    # Get screen size for boundary checking
    screen_width, _ = pydirectinput.size()
    window_width = 200

    label = tk.Label(root, text="", font=("Consolas", 12, "bold"), bg="#2E3440", fg="#ECEFF4", padx=10, pady=5, relief="solid", bd=1, anchor="center")
    label.pack(fill=tk.BOTH, expand=True)

    def update_position():
        x, y = pydirectinput.position()
        label.config(text=f"X: {x}, Y: {y}")
        
        # Calculate position offsets, adjusting for screen edges
        offset_x = 10
        offset_y = -60
        
        # If too close to right edge, position to the left
        if x + offset_x + window_width > screen_width:
            offset_x = -window_width - 10
        
        # If too close to top edge, position below the mouse
        if y + offset_y < 0:
            offset_y = 10
        
        root.geometry(f"+{x + offset_x}+{y + offset_y}")
        root.after(50, update_position)  # Update every 50ms

    update_position()
    root.mainloop()

if __name__ == "__main__":
    display_position()


