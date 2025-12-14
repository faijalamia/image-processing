import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Brightness & Contrast Adjuster")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Initialize variables
        self.image = None
        self.modified_image = None
        self.original_image = None
        self.image_path = None
        
        # Default values for adjustments
        self.brightness_value = 1.0  # Gamma correction value (1.0 means no change)
        self.contrast_value = 1.0    # CLAHE clip limit factor
        
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        
        # Left panel - Controls
        left_panel = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Title
        title_label = tk.Label(left_panel, text="Image Editor", font=("Arial", 24, "bold"), 
                               bg='#34495e', fg='#ecf0f1')
        title_label.pack(pady=(0, 30))
        
        # Open image button
        open_btn = tk.Button(left_panel, text="Open Image", command=self.open_image, 
                             bg='#3498db', fg='white', font=("Arial", 12), 
                             padx=20, pady=10, relief=tk.RAISED, cursor="hand2")
        open_btn.pack(pady=(0, 20))
        
        # Brightness control
        brightness_frame = tk.Frame(left_panel, bg='#34495e')
        brightness_frame.pack(fill=tk.X, pady=(0, 20))
        
        brightness_label = tk.Label(brightness_frame, text="Brightness", 
                                    font=("Arial", 14, "bold"), bg='#34495e', fg='#ecf0f1')
        brightness_label.pack(anchor=tk.W)
        
        self.brightness_slider = tk.Scale(brightness_frame, from_=0.1, to=3.0, 
                                          resolution=0.1, orient=tk.HORIZONTAL,
                                          length=250, command=self.update_brightness,
                                          bg='#34495e', fg='white', 
                                          highlightbackground='#34495e',
                                          troughcolor='#2c3e50', sliderrelief=tk.RAISED)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(fill=tk.X, pady=(10, 0))
        
        # Brightness value label
        self.brightness_val_label = tk.Label(brightness_frame, text="Value: 1.0", 
                                             bg='#34495e', fg='#bdc3c7', font=("Arial", 10))
        self.brightness_val_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Contrast control
        contrast_frame = tk.Frame(left_panel, bg='#34495e')
        contrast_frame.pack(fill=tk.X, pady=(0, 20))
        
        contrast_label = tk.Label(contrast_frame, text="Contrast (CLAHE)", 
                                  font=("Arial", 14, "bold"), bg='#34495e', fg='#ecf0f1')
        contrast_label.pack(anchor=tk.W)
        
        self.contrast_slider = tk.Scale(contrast_frame, from_=1.0, to=10.0, 
                                        resolution=0.5, orient=tk.HORIZONTAL,
                                        length=250, command=self.update_contrast,
                                        bg='#34495e', fg='white', 
                                        highlightbackground='#34495e',
                                        troughcolor='#2c3e50', sliderrelief=tk.RAISED)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X, pady=(10, 0))
        
        # Contrast value label
        self.contrast_val_label = tk.Label(contrast_frame, text="Value: 1.0", 
                                           bg='#34495e', fg='#bdc3c7', font=("Arial", 10))
        self.contrast_val_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Reset button
        reset_btn = tk.Button(left_panel, text="Reset Adjustments", command=self.reset_adjustments, 
                              bg='#e74c3c', fg='white', font=("Arial", 12), 
                              padx=20, pady=10, relief=tk.RAISED, cursor="hand2")
        reset_btn.pack(pady=(10, 20))
        
        # Save button
        save_btn = tk.Button(left_panel, text="Save Image", command=self.save_image, 
                             bg='#2ecc71', fg='white', font=("Arial", 12), 
                             padx=20, pady=10, relief=tk.RAISED, cursor="hand2")
        save_btn.pack(pady=(10, 0))
        
        # Instructions
        instructions_frame = tk.Frame(left_panel, bg='#34495e')
        instructions_frame.pack(fill=tk.X, pady=(30, 0))
        
        instructions_label = tk.Label(instructions_frame, text="Instructions:", 
                                      font=("Arial", 12, "bold"), bg='#34495e', fg='#ecf0f1')
        instructions_label.pack(anchor=tk.W)
        
        instructions_text = """
        1. Click 'Open Image' to load an image
        2. Adjust brightness with the top slider
        3. Adjust contrast with the bottom slider
        4. Click 'Save Image' to save your edits
        5. Click 'Reset' to revert to original
        """
        instructions = tk.Label(instructions_frame, text=instructions_text, 
                                justify=tk.LEFT, bg='#34495e', fg='#bdc3c7', font=("Arial", 10))
        instructions.pack(anchor=tk.W, pady=(10, 0))
        
        # Right panel - Image display
        right_panel = tk.Frame(self.root, bg='#1c2833', padx=10, pady=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Image display label
        self.image_label = tk.Label(right_panel, text="No Image Loaded", 
                                    bg='#1c2833', fg='#7f8c8d', font=("Arial", 16))
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#34495e', fg='#ecf0f1')
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
    
    def open_image(self):
        """Open an image file using file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), 
                       ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Read the image using OpenCV
                self.image = cv2.imread(file_path)
                if self.image is None:
                    raise ValueError("Could not read the image file")
                
                # Store a copy of the original image
                self.original_image = self.image.copy()
                self.modified_image = self.image.copy()
                self.image_path = file_path
                
                # Convert from BGR to RGB for display
                image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                
                # Resize image if it's too large for display
                display_image = self.resize_image_for_display(image_rgb)
                
                # Convert to ImageTk format
                pil_image = Image.fromarray(display_image)
                self.tk_image = ImageTk.PhotoImage(pil_image)
                
                # Update the image label
                self.image_label.config(image=self.tk_image, text="")
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                
                # Reset sliders to default values
                self.reset_adjustments()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def resize_image_for_display(self, image):
        """Resize image to fit in the display area while maintaining aspect ratio"""
        # Get the size of the display area
        display_width = self.image_label.winfo_width() or 600
        display_height = self.image_label.winfo_height() or 600
        
        # If the display area is very small, use defaults
        if display_width < 100 or display_height < 100:
            display_width, display_height = 600, 600
        
        # Get the original dimensions
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale = min(display_width / width, display_height / height)
        
        if scale < 1:  # Only resize if image is larger than display area
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    def update_brightness(self, value):
        """Apply gamma correction for brightness adjustment"""
        self.brightness_value = float(value)
        self.brightness_val_label.config(text=f"Value: {self.brightness_value:.1f}")
        self.apply_adjustments()
    
    def update_contrast(self, value):
        """Apply CLAHE for contrast adjustment"""
        self.contrast_value = float(value)
        self.contrast_val_label.config(text=f"Value: {self.contrast_value:.1f}")
        self.apply_adjustments()
    
    def apply_adjustments(self):
        """Apply both brightness and contrast adjustments"""
        if self.original_image is None:
            return
        
        # Apply brightness adjustment using gamma correction
        if self.brightness_value != 1.0:
            # Gamma correction formula
            gamma = 1.0 / self.brightness_value
            # Build a lookup table mapping the pixel values [0, 255] to their adjusted gamma values
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            # Apply gamma correction using the lookup table
            brightness_adjusted = cv2.LUT(self.original_image, table)
        else:
            brightness_adjusted = self.original_image.copy()
        
        # Apply contrast adjustment using CLAHE
        if self.contrast_value > 1.0:
            # Convert to LAB color space to apply CLAHE to the L channel only
            lab = cv2.cvtColor(brightness_adjusted, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=self.contrast_value, tileGridSize=(8, 8))
            cl = clahe.apply(l_channel)
            
            # Merge the CLAHE enhanced L channel back with a and b channels
            merged = cv2.merge((cl, a, b))
            
            # Convert back to BGR color space
            contrast_adjusted = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        else:
            contrast_adjusted = brightness_adjusted
        
        # Store the modified image
        self.modified_image = contrast_adjusted
        
        # Convert from BGR to RGB for display
        image_rgb = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2RGB)
        
        # Resize for display if needed
        display_image = self.resize_image_for_display(image_rgb)
        
        # Convert to ImageTk format
        pil_image = Image.fromarray(display_image)
        self.tk_image = ImageTk.PhotoImage(pil_image)
        
        # Update the image label
        self.image_label.config(image=self.tk_image)
        
        # Update status
        self.update_status(f"Applied adjustments: Brightness={self.brightness_value:.1f}, Contrast={self.contrast_value:.1f}")
    
    def reset_adjustments(self):
        """Reset all adjustments to default values"""
        if self.original_image is not None:
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.brightness_val_label.config(text="Value: 1.0")
            self.contrast_val_label.config(text="Value: 1.0")
            self.brightness_value = 1.0
            self.contrast_value = 1.0
            
            # Reset to original image
            self.modified_image = self.original_image.copy()
            
            # Convert from BGR to RGB for display
            image_rgb = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2RGB)
            
            # Resize for display if needed
            display_image = self.resize_image_for_display(image_rgb)
            
            # Convert to ImageTk format
            pil_image = Image.fromarray(display_image)
            self.tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update the image label
            self.image_label.config(image=self.tk_image)
            
            self.update_status("Reset to original image")
    
    def save_image(self):
        """Save the modified image to a file"""
        if self.modified_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), 
                       ("PNG files", "*.png"), 
                       ("BMP files", "*.bmp"),
                       ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Save the image
                cv2.imwrite(file_path, self.modified_image)
                self.update_status(f"Image saved to: {file_path}")
                messagebox.showinfo("Success", f"Image saved successfully!\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()