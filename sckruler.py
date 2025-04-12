#09/03/2025 by Sercan Cikintoglu
#TODO: toolbar icon
#TODO: first position
#TODO: call without terminal

import tkinter as tk
import os
#import subprocess

class ScreenRuler(tk.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)  # Removes title bar
        
        # Force Ubuntu to recognize as a normal application
#        self.wm_attributes("-type", "normal")  # Register as normal window
#        icon_path = os.path.abspath("ruler.png")
#        if os.path.exists(icon_path):
#            self.iconphoto(False, tk.PhotoImage(file=icon_path))

        # Ensure it keeps focus
#        self.after(100, self.register_with_ubuntu)  # Forces Ubuntu to recognize it        

        self.title("Screen Ruler")
        self.minsize(200, 60)  # Adjust for vertical mode
        self.geometry("200x60")
        self.is_vertical = False  # Track rotation state

        # Auto-detect screen DPI
        self.dpi = self.winfo_fpixels("1i")  

        # Default unit settings
        self.unit       = "Pixels"
        self.unitshorts = {'Pixels':'px', 'Centimeters':'cm', 'Inches':'in'}        
        self.bgclr      = "#FFA500"

        # Enable dragging from anywhere
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.on_move)

        # Pop-up menu for options
        self.unit_var = tk.StringVar(value=self.unit)
        self.unit_var.trace_add('write', self.change_unit)
        self.clickmenu = tk.Menu(self, tearoff=0)
        self.clickmenu.add_radiobutton(label="Pixels", value="Pixels", variable=self.unit_var)
        self.clickmenu.add_radiobutton(label="Centimeters", value="Centimeters", variable=self.unit_var)
        self.clickmenu.add_radiobutton(label="Inches", value="Inches", variable=self.unit_var)
        self.clickmenu.add_separator()
        self.clickmenu.add_command(label="Rotate", command=self.toggle_orientation)
        self.clickmenu.add_separator()
        self.clickmenu.add_command(label="Close", command=self.destroy)
        self.bind("<Button-3>", self.do_popup)

        # Create a resizable canvas
        self.canvas = tk.Canvas(self, bg=self.bgclr)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind resize event
        self.bind("<Configure>", self.update_ruler)

        # Enable resizing
        if self.is_vertical:
          self.resizer = tk.Frame(self, bg="#B22222", cursor="sb_v_double_arrow")
          self.resizer.place(relx=0.5, rely=1.0, anchor="n", width=10, height=30)
        else:
          self.resizer = tk.Frame(self, bg="#B22222", cursor="sb_h_double_arrow")
          self.resizer.place(relx=1.0, rely=0.5, anchor="e", width=10, height=30)


        self.resizer.bind("<B1-Motion>", self.on_resize)


#    def register_with_ubuntu(self):
#        """Forces Ubuntu to recognize the application for Dock and Alt+Tab."""
#        try:
#            # Get the window ID using wm_frame()
#            window_id = self.winfo_id()

#            # Use xdotool to set the window class
#            subprocess.run(["xdotool", "set_window", "--classname", "SckRuler", str(window_id)], check=True)
#        except Exception as e:
#            print("xdotool failed:", e)

    def do_popup(self, event):
        """Show right-click menu."""
        try:
            self.clickmenu.tk_popup(event.x_root, event.y_root)
        finally:
            self.clickmenu.grab_release()

    def start_move(self, event):
        """Records the initial position when moving starts."""
        if event.widget == self.resizer:
           return  # Don't trigger dragging if clicking the resizer
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """Moves the window by dragging."""
        if event.widget == self.resizer:
           return  # Don't trigger dragging if clicking the resizer        
        self.geometry(f"+{event.x_root - self.x}+{event.y_root - self.y}")

    def on_resize(self, event):
        """Resizes the window when dragging the resizer (adjusts width/height based on orientation)."""
        if self.is_vertical:
            new_height = event.y_root - self.winfo_y()
            self.geometry(f"{self.winfo_width()}x{new_height}")
        else:
            new_width = event.x_root - self.winfo_x()
            self.geometry(f"{new_width}x{self.winfo_height()}")

    def change_unit(self, *args):
        """Change the unit and update the ruler."""
        self.unit = self.unit_var.get()
        self.update_ruler()

    def toggle_orientation(self):
        """Switch between horizontal and vertical orientation."""
        self.is_vertical = not self.is_vertical
        if self.is_vertical:
            self.minsize(60, 200)
            self.geometry(f"60x{self.winfo_width()}")       # Swap width & height
            self.resizer.config(cursor="sb_v_double_arrow") # Change resize cursor
            self.resizer.place(relx=0.5, rely=1.0, anchor="s", width=30, height=10) #Place resizer  
        else:
            self.minsize(200, 60)
            self.geometry(f"{self.winfo_height()}x60")
            self.resizer.config(cursor="sb_h_double_arrow")
            self.resizer.place(relx=1.0, rely=0.5, anchor="e", width=10, height=30)

        self.update_ruler()

    def convert_to_pixels(self, value):
        """Convert cm or inches to pixels using detected DPI."""
        if self.unit == "Centimeters":
            return value * (self.dpi / 2.54)  # 1 cm = 2.54 inches
        elif self.unit == "Inches":
            return value * self.dpi  # 1 inch = DPI pixels
        else:
            return 100 * value  # Pixels stay the same

    def update_ruler(self, event=None):
        """Redraws the ruler dynamically based on window orientation."""
        self.canvas.delete("all")
        size = self.winfo_height() if self.is_vertical else self.winfo_width()
        unit_size = self.convert_to_pixels(1)
        if self.is_vertical:
           self.canvas.create_text(30,5, text=self.unitshorts[self.unit], anchor="n", font=("Arial", 12))        
        else:
           self.canvas.create_text(5,30, text=self.unitshorts[self.unit], anchor="w", font=("Arial", 12))

        i = 0

        while i < size:
            if self.is_vertical:
                # Vertical ruler
                self.canvas.create_line(0, i, 20, i, fill="black", width=2)
                self.canvas.create_line(40, i, 60, i, fill="black", width=2)
                j = i + unit_size / 10.0
                while j < i + unit_size:
                    self.canvas.create_line(0, j, 10, j, fill="black", width=1)
                    self.canvas.create_line(50, j, 60, j, fill="black", width=1)
                    j += unit_size / 10.0
                self.canvas.create_line(0, i + unit_size / 2.0, 15, i + unit_size / 2.0, fill="black", width=2)
                self.canvas.create_line(45, i + unit_size / 2.0, 60, i + unit_size / 2.0, fill="black", width=2)
                if i > 0:
                    text = str("%g" % (i / unit_size)) if self.unit != "Pixels" else str(i)
                    self.canvas.create_text(30, i, text=text, anchor="center", font=("Arial", 12), angle=90)
            else:
                # Horizontal ruler
                self.canvas.create_line(i, 0, i, 20, fill="black", width=2)
                self.canvas.create_line(i, 40, i, 60, fill="black", width=2)
                j = i + unit_size / 10.0
                while j < i + unit_size:
                    self.canvas.create_line(j, 0, j, 10, fill="black", width=1)
                    self.canvas.create_line(j, 50, j, 60, fill="black", width=1)
                    j += unit_size / 10.0
                self.canvas.create_line(i + unit_size / 2.0, 0, i + unit_size / 2.0, 15, fill="black", width=2)
                self.canvas.create_line(i + unit_size / 2.0, 45, i + unit_size / 2.0, 60, fill="black", width=2)
                if i > 0:
                    text = str("%g" % (i / unit_size)) if self.unit != "Pixels" else str(i)
                    self.canvas.create_text(i, 30, text=text, anchor="center", font=("Arial", 12))

            i += unit_size

if __name__ == "__main__":
    app = ScreenRuler()
    app.mainloop()
