import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, colorchooser
from tkinter import Menu, Checkbutton, IntVar, Scrollbar, Frame, Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageSequence, ImageOps, ImageEnhance, ImageFilter
import os
import random
import platform
import threading
import time
import cv2

class GIFEditor:
    def __init__(self, master):
        """Initialize the GIF editor with the main window and UI setup."""
        self.master = master
        self.master.title("GIFCraft - GIF Editor")
        self.master.geometry("800x600")

        # Initial settings
        self.frame_index = 0
        self.frames = []
        self.delays = []
        self.is_playing = False
        self.history = []
        self.redo_stack = []
        self.current_file = None
        self.checkbox_vars = []
        self.check_all = tk.BooleanVar(value=False)
        self.is_preview_mode = False
        self.preview_width = 200
        self.preview_height = 150

        # Draw mode settings
        self.is_draw_mode = False
        self.brush_color = "#000000"
        self.brush_size = 5
        self.tool = 'brush'
        self.is_drawing = False
        self.last_x = None
        self.last_y = None

        # Setup UI and bindings
        self.setup_ui()
        self.bind_keyboard_events()

    def update_title(self):
        """Update the window title to reflect the current file state."""
        if self.frames:
            title = f"GIFCraft - GIF Editor - {os.path.basename(self.current_file)}" if self.current_file else "GIFCraft - GIF Editor - Unsaved File"
            self.master.title(title)
        else:
            self.master.title("GIFCraft - GIF Editor")

    def setup_ui(self):
        """Set up the user interface."""
        self.setup_menu()
        self.setup_frame_list()
        self.setup_control_frame()

    def setup_menu(self):
        """Set up the menu bar."""
        self.menu_bar = Menu(self.master)
        self.create_file_menu()
        self.create_edit_menu()
        self.create_effects_menu()
        self.create_animation_menu()
        self.create_help_menu()
        self.master.config(menu=self.menu_bar)

    def create_file_menu(self):
        """Create the File menu."""
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Load GIF/PNG/WebP", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As High Quality GIF", command=self.save_as_high_quality_gif)
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Extract Video Frames", command=self.extract_video_frames)
        file_menu.add_command(label="Extract Frames Gif", command=self.extract_frames_gif)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

    def create_edit_menu(self):
        """Create the Edit menu."""
        edit_menu = Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Merge Selected Frames", command=self.merge_frames)
        edit_menu.add_command(label="Add Image", command=self.add_image)
        edit_menu.add_command(label="Add Text", command=self.add_text_frame)
        edit_menu.add_command(label="Apply Frame 1", command=self.apply_frame_1_)
        edit_menu.add_command(label="Add Overlay Frame", command=self.apply_overlay_frame)
        edit_menu.add_command(label="Add Empty Frame", command=self.add_empty_frame)
        edit_menu.add_command(label="Delete Frame(s)", command=self.delete_frames, accelerator="Del")
        edit_menu.add_command(label="Delete Unchecked Frame(s)", command=self.delete_unchecked_frames, accelerator="Ctrl+Del") 
        edit_menu.add_separator()
        edit_menu.add_command(label="Move Selected Frames", command=self.prompt_and_move_selected_frames)
        edit_menu.add_command(label="Move Frame Up", command=self.move_frame_up, accelerator="Arrow Up")
        edit_menu.add_command(label="Move Frame Down", command=self.move_frame_down, accelerator="Arrow Down")
        edit_menu.add_separator()        
        edit_menu.add_command(label="Rotate Selected Frames 180º", command=self.rotate_selected_frames_180)
        edit_menu.add_command(label="Rotate Selected Frames 90º CW", command=self.rotate_selected_frames_90_cw)
        edit_menu.add_command(label="Rotate Selected Frames 90º CCW", command=self.rotate_selected_frames_90_ccw)
        edit_menu.add_command(label="Rotate Selected Frames...", command=self.rotate_selected_frames)
        edit_menu.add_separator()
        edit_menu.add_command(label="Flip Selected Frames Horizontal", command=self.flip_selected_frames_horizontal)
        edit_menu.add_command(label="Flip Selected Frames Vertical", command=self.flip_selected_frames_vertical)
        edit_menu.add_separator()
        edit_menu.add_command(label="Check/Uncheck All", command=self.toggle_check_all, accelerator="A")
        edit_menu.add_command(label="Check Even or Odd Frames", command=self.mark_even_odd_frames)
        edit_menu.add_command(label="Check Frames Relative to Cursor", command=self.mark_frames_relative_to_cursor)
        edit_menu.add_command(label="Go to Frame", command=self.go_to_frame)
        edit_menu.add_separator()
        edit_menu.add_command(label="Crop Frames", command=self.crop_frames)
        edit_menu.add_command(label="Resize Frames", command=self.resize_frames_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_frames, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_frames, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

    def create_effects_menu(self):
        """Create the Effects menu."""
        effects_menu = Menu(self.menu_bar, tearoff=0)
        effects_menu.add_command(label="Crossfade Effect", command=self.crossfade_effect)
        effects_menu.add_command(label="Reverse Frames", command=self.reverse_frames)
        effects_menu.add_command(label="Desaturate Frames", command=self.desaturate_frames)
        effects_menu.add_command(label="Sharpness Effect", command=self.apply_sharpening_effect)
        effects_menu.add_command(label="Strange Sharpness Effect", command=self.apply_strange_sharpening_effect)
        effects_menu.add_command(label="Ghost Detection Effect", command=self.ghost_detection_effect) 
        effects_menu.add_command(label="Invert Colors", command=self.invert_colors_of_selected_frames)
        effects_menu.add_command(label="Glitch Effect", command=self.apply_random_glitch_effect)
        effects_menu.add_command(label="Sketch Effect", command=self.apply_sketch_effect)
        effects_menu.add_command(label="Adjust Brightness and Contrast", command=self.prompt_and_apply_brightness_contrast)
        effects_menu.add_command(label="Adjust Hue, Saturation, and Lightness", command=self.adjust_hsl)
        effects_menu.add_command(label="Zoom Effect", command=self.apply_zoom_effect)
        effects_menu.add_command(label="Apply Zoom Effect Click", command=self.apply_zoom_effect_click)
        effects_menu.add_command(label="Blur Effect", command=self.apply_blur_effect)
        effects_menu.add_command(label="Zoom and Speed Blur Effect", command=self.apply_zoom_and_speed_blur_effect) 
        effects_menu.add_command(label="Noise Effect", command=self.apply_noise_effect)
        effects_menu.add_command(label="Pixelate Effect", command=self.apply_pixelate_effect)
        effects_menu.add_command(label="Reduce Transparency", command=self.reduce_transparency_of_checked_frames)
        effects_menu.add_command(label="Slide Transition Effect", command=self.slide_transition_effect)
        self.menu_bar.add_cascade(label="Effects", menu=effects_menu)

    def create_animation_menu(self):
        """Create the Animation menu."""
        animation_menu = Menu(self.menu_bar, tearoff=0)
        animation_menu.add_command(label="Play/Stop Animation", command=self.toggle_play_pause, accelerator="Space")
        animation_menu.add_command(label="Change Preview Resolution", command=self.change_preview_resolution)
        animation_menu.add_command(label="Transparent Frames Preview", command=self.toggle_transparent_frames_preview, accelerator="T")
        animation_menu.add_command(label="Draw Mode", command=self.toggle_draw_mode, accelerator="W")
        self.menu_bar.add_cascade(label="Animation", menu=animation_menu)

    def create_help_menu(self):
        """Create the Help menu."""
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def new_file(self, event=None):
        """Create a new file, prompting to save unsaved changes if any."""
        if self.frames:
            response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save the current file before creating a new one?")
            if response:  # Yes
                self.save()
                if self.frames:  # If saving was cancelled or failed, do not proceed
                    return
            elif response is None:  # Cancel
                return

        # Reset the editor state for a new file
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        self.current_file = None
        self.frame_index = 0
        self.base_size = None  # Clear the base size
        self.update_frame_list()
        self.show_frame()
        self.update_title()

    def load_file(self, event=None):
        """Load a GIF, PNG, or WebP file and extract its frames."""
        if self.frames:
            response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save the current file before loading a new one?")
            if response:  # Yes
                self.save()
                if self.frames:  # If saving was cancelled or failed, do not proceed
                    return
            elif response is None:  # Cancel
                return

        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.gif *.png *.webp")])
        if not file_path:
            return

        self.save_state()  # Save the state before making changes
        self.frames = []
        self.delays = []
        self.checkbox_vars = []
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        try:
            with Image.open(file_path) as img:
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    if i == 0:
                        self.base_size = frame.size  # Store the size of the first frame
                    self.frames.append(self.resize_to_base_size(frame.copy()))
                    delay = int(frame.info.get('duration', 100))  # Ensure delay is always an integer
                    self.delays.append(delay)
                    var = IntVar()
                    var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                    self.checkbox_vars.append(var)
            self.frame_index = 0
            self.update_frame_list()
            self.show_frame()
            self.current_file = file_path
            self.update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def save(self, event=None):
        """Save the current frames and delays to a GIF file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as()

    def save_as(self, event=None):
        """Save the current frames and delays to a file with the selected format."""
        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif"), ("PNG files", "*.png"), ("WebP files", "*.webp")])
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.update_title()

    def save_as_high_quality_gif(self):
        """Save the current frames and delays to a high-quality GIF file using dithering."""
        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if file_path:
            try:
                images = [frame.convert("RGB").quantize(method=0) for frame in self.frames]
                images[0].save(file_path, save_all=True, append_images=images[1:], duration=self.delays, loop=0, dither=Image.NONE)
                self.current_file = file_path
                self.update_title()
                messagebox.showinfo("Success", "High-quality GIF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save high-quality GIF: {e}")

    def extract_video_frames(self):
        """Extract frames from a video file and save them as images with progress tracking and cancel option."""
        # Ask the user to select a video file
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        if not file_path:
            return

        # Ask the user to select a directory to save the frames
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        def cancel_extraction():
            nonlocal cancel
            cancel = True

        def extract_frames():
            nonlocal cancel
            start_time = time.time()

            try:
                cap = cv2.VideoCapture(file_path)
                if not cap.isOpened():
                    messagebox.showerror("Error", "Failed to open video file.")
                    progress_window.destroy()
                    return

                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                extracted_frames = 0
                success, frame = cap.read()

                while success and not cancel:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)
                    frame_path = os.path.join(output_dir, f"frame_{extracted_frames + 1}.png")
                    image.save(frame_path)
                    extracted_frames += 1

                    progress_var.set((extracted_frames / frame_count) * 100)
                    progress_window.update_idletasks()
                    success, frame = cap.read()

                cap.release()
                end_time = time.time()
                elapsed_time = end_time - start_time

                if cancel:
                    messagebox.showinfo("Cancelled", "Frame extraction cancelled.")
                else:
                    messagebox.showinfo("Success", f"Extracted {extracted_frames} frames in {elapsed_time:.2f} seconds!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract frames: {e}")
            finally:
                progress_window.destroy()

        cancel = False

        progress_window = tk.Toplevel(self.master)
        progress_window.title("Extracting Frames")
        progress_window.geometry("300x100")
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        cancel_button = tk.Button(progress_window, text="Cancel", command=cancel_extraction)
        cancel_button.pack(pady=10)

        extraction_thread = threading.Thread(target=extract_frames)
        extraction_thread.start()

    def extract_frames_gif(self):
        """Extract the frames and save them as individual images."""
        if not self.frames:
            messagebox.showerror("Error", "No frames to extract.")
            return

        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        try:
            for i, frame in enumerate(self.frames):
                frame_path = os.path.join(folder_path, f"frame_{i + 1}.png")
                frame.save(frame_path)
            messagebox.showinfo("Success", "Frames extracted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract frames: {e}")

    def save_to_file(self, file_path):
        """Save the frames and delays to the specified file in the given format."""
        if self.frames:
            try:
                _, ext = os.path.splitext(file_path)
                ext = ext[1:].lower()  # Remove the dot and convert to lowercase
                if ext == 'gif':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0)
                elif ext == 'png':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0, format='PNG')
                elif ext == 'webp':
                    self.frames[0].save(file_path, save_all=True, append_images=self.frames[1:], duration=self.delays, loop=0, format='WEBP')
                else:
                    messagebox.showerror("Error", f"Unsupported file format: {ext.upper()}")
                    return
                self.current_file = file_path
                self.update_title()
                messagebox.showinfo("Success", f"{ext.upper()} saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {ext.upper()}: {e}")

    def merge_frames(self):
        """Merge the checked frames from top to bottom respecting transparency."""
        self.save_state()  # Save the state before making changes

        # Find the indices of the checked frames
        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not checked_indices:
            messagebox.showinfo("Info", "No frames selected for merging.")
            return

        # Merge the frames
        base_frame = self.frames[checked_indices[0]].copy()
        for index in checked_indices[1:]:
            frame = self.frames[index]
            base_frame = Image.alpha_composite(base_frame, frame)

        # Replace the first checked frame with the merged frame
        self.frames[checked_indices[0]] = base_frame
        # Remove the other checked frames
        for index in reversed(checked_indices[1:]):
            del self.frames[index]
            del self.delays[index]
            del self.checkbox_vars[index]

        self.frame_index = checked_indices[0]
        self.update_frame_list()
        self.show_frame()
        messagebox.showinfo("Success", "Frames merged successfully!")

    def add_image(self):
        """Add images to the frames."""
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.gif *.bmp")])
        if not file_paths:
            return

        self.save_state()  # Save the state before making changes
        try:
            for file_path in file_paths:
                with Image.open(file_path) as image:
                    # Resize the new image to match the base dimensions
                    if not self.frames:  # If no frames, set the base size to the first image's size
                        self.base_size = image.size
                    image = self.resize_to_base_size(image.copy())
                    self.frames.append(image)
                self.delays.append(100)  # Default delay for added images
                var = IntVar()
                var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
                self.checkbox_vars.append(var)

            self.update_frame_list()
            self.show_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add images: {e}")

    def add_text_frame(self):
        """Create a frame with text using user inputs for font, size, color, outline, and position."""
        
        # Ensure there are frames to use as a reference for mouse positioning
        if len(self.frames) < 1:
            messagebox.showerror("Error", "There are no frames available to use as a reference.")
            return

        def get_system_fonts():
            """Retrieve a list of system fonts available on the user's machine."""
            font_dirs = []
            if platform.system() == "Windows":
                windir = os.environ.get('WINDIR')
                if windir:
                    font_dirs = [os.path.join(windir, 'Fonts')]
            elif platform.system() == "Darwin":  # macOS
                font_dirs = ["/Library/Fonts", "~/Library/Fonts"]
            elif platform.system() == "Linux":
                font_dirs = ["/usr/share/fonts", "~/.local/share/fonts", "~/.fonts"]

            fonts = set()
            for font_dir in font_dirs:
                font_dir = os.path.expanduser(font_dir)
                if os.path.isdir(font_dir):
                    for root, _, files in os.walk(font_dir):
                        for file in files:
                            if file.lower().endswith(('.ttf', '.otf')):
                                fonts.add(os.path.join(root, file))
            return sorted(fonts, key=lambda f: os.path.basename(f).lower())

        fonts = get_system_fonts()
        font_names = [os.path.basename(f).replace('.ttf', '').replace('.otf', '') for f in fonts]
        default_font = None

        if platform.system() == 'Windows':
            default_font = 'arial'
        elif platform.system() == 'Darwin':
            default_font = next((f for f in font_names if 'arial' in f.lower()), None)
        elif platform.system() == 'Linux':
            default_font = next((f for f in font_names if 'dejavusans' in f.lower()), None)

        if not default_font and fonts:
            default_font = font_names[0]

        if not fonts:
            messagebox.showerror("Error", "No fonts found on the system.")
            return

        # Create a new window for text input
        top = tk.Toplevel(self.master)
        top.title("Add Text to Frame")

        # Preview font label
        font_preview_label = tk.Label(top, text="Sample Text", font=(default_font, 14))
        font_preview_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        # Entry for text
        tk.Label(top, text="Enter text to display:").grid(row=1, column=0, padx=10, pady=5)
        text_entry = tk.Entry(top, width=30)
        text_entry.grid(row=1, column=1, padx=10, pady=5)

        # Font selection with preview
        tk.Label(top, text="Choose Font:").grid(row=2, column=0, padx=10, pady=5)
        font_combobox = ttk.Combobox(top, values=font_names, width=28)
        font_combobox.set(default_font)
        font_combobox.grid(row=2, column=1, padx=10, pady=5)

        def update_font_preview(event):
            selected_font_name = font_combobox.get()
            selected_font_path = next((f for f in fonts if os.path.basename(f).replace('.ttf', '').replace('.otf', '') == selected_font_name), None)
            if selected_font_path:
                try:
                    preview_font = ImageFont.truetype(selected_font_path, 14)
                    font_preview_label.config(font=(selected_font_name, 14))
                except IOError:
                    font_preview_label.config(font=("Arial", 14))
            else:
                font_preview_label.config(font=("Arial", 14))

        font_combobox.bind("<<ComboboxSelected>>", update_font_preview)

        # Font size
        tk.Label(top, text="Enter font size (in pixels):").grid(row=3, column=0, padx=10, pady=5)
        font_size_entry = tk.Entry(top, width=30)
        font_size_entry.grid(row=3, column=1, padx=10, pady=5)
        font_size_entry.insert(0, "20")

        # Bold and Italic checkboxes
        bold_var = tk.BooleanVar()
        italic_var = tk.BooleanVar()
        tk.Checkbutton(top, text="Bold", variable=bold_var).grid(row=4, column=0, padx=10, pady=5)
        tk.Checkbutton(top, text="Italic", variable=italic_var).grid(row=4, column=1, padx=10, pady=5)

        # Text color
        tk.Label(top, text="Choose text color:").grid(row=5, column=0, padx=10, pady=5)
        text_color_button = tk.Button(top, text="Select Color")
        text_color_button.grid(row=5, column=1, padx=10, pady=5)

        text_color = "#FFFFFF"
        def choose_text_color():
            nonlocal text_color
            color_code = colorchooser.askcolor(title="Choose text color")
            if color_code:
                text_color = color_code[1]

        text_color_button.config(command=choose_text_color)

        # Outline color
        tk.Label(top, text="Choose outline color:").grid(row=6, column=0, padx=10, pady=5)
        outline_color_button = tk.Button(top, text="Select Color")
        outline_color_button.grid(row=6, column=1, padx=10, pady=5)

        outline_color = "#000000"
        def choose_outline_color():
            nonlocal outline_color
            color_code = colorchooser.askcolor(title="Choose outline color")
            if color_code:
                outline_color = color_code[1]

        outline_color_button.config(command=choose_outline_color)

        # Outline thickness
        tk.Label(top, text="Enter outline thickness (0 to 5):").grid(row=7, column=0, padx=10, pady=5)
        outline_thickness_entry = tk.Entry(top, width=30)
        outline_thickness_entry.grid(row=7, column=1, padx=10, pady=5)

        # Text position
        tk.Label(top, text="Choose text position:").grid(row=8, column=0, padx=10, pady=5)
        position_options = ["Top", "Center", "Bottom", "Mouse"]
        position_combobox = ttk.Combobox(top, values=position_options, width=28)
        position_combobox.set("Center")
        position_combobox.grid(row=8, column=1, padx=10, pady=5)

        # Margin input
        tk.Label(top, text="Enter margin (default is 30):").grid(row=9, column=0, padx=10, pady=5)
        margin_entry = tk.Entry(top, width=30)
        margin_entry.grid(row=9, column=1, padx=10, pady=5)
        margin_entry.insert(0, "30")

        def submit():
            text = text_entry.get()
            font_choice = font_combobox.get()
            font_size = font_size_entry.get()
            outline_thickness = outline_thickness_entry.get()
            position_choice = position_combobox.get().lower()
            margin = margin_entry.get()

            if not text or not font_choice or not font_size.isdigit() or not outline_thickness.isdigit() or not margin.isdigit():
                messagebox.showerror("Error", "Please fill all fields correctly.")
                return

            font_path = next((f for f in fonts if os.path.basename(f).replace('.ttf', '').replace('.otf', '') == font_choice), default_font)
            font_size = int(font_size)
            outline_thickness = int(outline_thickness)
            margin = int(margin)
            bold = bold_var.get()
            italic = italic_var.get()

            if bold and italic:
                font_style = "bolditalic"
            elif bold:
                font_style = "bold"
            elif italic:
                font_style = "italic"
            else:
                font_style = "regular"

            # Create a new transparent frame
            base_size = self.frames[0].size
            new_frame = Image.new("RGBA", base_size, (0, 0, 0, 0))

            # Load the font
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                messagebox.showerror("Error", f"Failed to load font: {font_choice}. Using default font.")
                font = ImageFont.truetype(default_font, font_size)

            draw = ImageDraw.Draw(new_frame)

            # Calculate text size and position
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

            # Ensure the text stays within the frame dimensions
            if position_choice == "top":
                text_position = (max(0, (base_size[0] - text_width) // 2), margin)
            elif position_choice == "center":
                text_position = (max(0, (base_size[0] - text_width) // 2), max(0, (base_size[1] - text_height) // 2))
            elif position_choice == "bottom":
                text_position = (max(0, (base_size[0] - text_width) // 2), base_size[1] - text_height - margin)
                # Ensure the text stays within the frame dimensions
                if text_position[1] + text_height > base_size[1] - margin:
                    text_position = (text_position[0], base_size[1] - text_height - margin)
            elif position_choice == "mouse":
                # Use the first frame as reference for mouse positioning
                ref_frame = self.frames[0].copy()
                ref_image = ImageTk.PhotoImage(ref_frame)

                mouse_top = tk.Toplevel(self.master)
                mouse_top.title("Click to Position Text")
                canvas = tk.Canvas(mouse_top, width=ref_frame.width, height=ref_frame.height)
                canvas.pack()
                canvas.create_image(0, 0, anchor=tk.NW, image=ref_image)

                text_position = [0, 0]

                def on_click(event):
                    text_position[0] = min(max(0, event.x - text_width // 2), base_size[0] - text_width)
                    text_position[1] = min(max(0, event.y - text_height // 2), base_size[1] - text_height)
                    mouse_top.destroy()

                canvas.bind("<Button-1>", on_click)
                self.master.wait_window(mouse_top)

            # Draw text with outline
            if outline_thickness > 0:
                for dx in range(-outline_thickness, outline_thickness + 1):
                    for dy in range(-outline_thickness, outline_thickness + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_position[0] + dx, text_position[1] + dy), text, font=font, fill=outline_color)
            draw.text(text_position, text, font=font, fill=text_color)

            # Add the new frame to the frames list at the first position
            self.frames.insert(0, new_frame)
            self.delays.insert(0, 100)  # Default delay for new frame
            var = tk.IntVar()
            var.trace_add('write', lambda *args, i=0: self.set_current_frame(i))
            self.checkbox_vars.insert(0, var)

            self.update_frame_list()
            self.show_frame()
            top.destroy()

        tk.Button(top, text="Add Text", command=submit).grid(row=10, column=0, columnspan=2, pady=10)

    def apply_frame_1_(self):
        """Apply the content of Frame 1 to all checked frames, respecting the transparency of Frame 1."""
        if not self.frames:
            messagebox.showerror("Error", "No frames available to apply the effect.")
            return

        if not self.checkbox_vars[0].get():
            messagebox.showinfo("Info", "Frame 1 is not checked. Please check Frame 1 to use it as the source frame.")
            return

        frame_1 = self.frames[0].convert("RGBA")

        for i, var in enumerate(self.checkbox_vars):
            if i != 0 and var.get() == 1:
                target_frame = self.frames[i].convert("RGBA")
                combined_frame = Image.alpha_composite(target_frame, frame_1)
                self.frames[i] = combined_frame

        self.update_frame_list()
        self.show_frame()

    def apply_overlay_frame(self):
        """Apply an overlay frame (watermark or border) to the selected frames with user-defined transparency."""
        overlay_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if not overlay_file:
            return

        # Prompt the user for the transparency intensity
        intensity = simpledialog.askfloat("Overlay Frame Transparency", "Enter transparency intensity (0.0 to 1.0):", minvalue=0.0, maxvalue=1.0)
        if intensity is None:
            return  # User canceled the dialog

        # Prompt the user whether to distort the overlay image to match the frame size
        distort_overlay = messagebox.askyesno("Distort Overlay", "Do you want to distort the overlay image to match the frame size?")

        self.save_state()  # Save the state before making changes

        try:
            overlay_image = Image.open(overlay_file).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load overlay image: {e}")
            return

        def apply_transparent_overlay(frame, overlay, intensity, distort):
            """Apply the overlay to the frame using the given intensity, respecting transparency."""
            frame = frame.convert("RGBA")
            overlay = overlay.copy()
            
            if distort:
                overlay = overlay.resize(frame.size, Image.LANCZOS)
            else:
                # Center the overlay if not distorting
                overlay_width, overlay_height = overlay.size
                frame_width, frame_height = frame.size
                x_offset = (frame_width - overlay_width) // 2
                y_offset = (frame_height - overlay_height) // 2
                new_overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                new_overlay.paste(overlay, (x_offset, y_offset))
                overlay = new_overlay
            
            # Extract the alpha channel and apply intensity
            alpha = overlay.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(intensity)
            overlay.putalpha(alpha)
            
            return Image.alpha_composite(frame, overlay)

        # Apply the overlay frame to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i].convert("RGBA")
                self.frames[i] = apply_transparent_overlay(frame, overlay_image, intensity, distort_overlay)

        self.update_frame_list()
        self.show_frame()

    def add_empty_frame(self):
        """Add an empty frame with an optional background color. If there are no frames, prompt for the size of the new frame."""
        if not self.frames:
            # Prompt the user for the width and height if no frames exist
            width = simpledialog.askinteger("Frame Size", "Enter frame width:", minvalue=1)
            height = simpledialog.askinteger("Frame Size", "Enter frame height:", minvalue=1)
            if not width or not height:
                messagebox.showerror("Invalid Input", "Width and height must be positive integers.")
                return
            frame_size = (width, height)

            # Prompt the user for the background color in hexadecimal format
            color_code = simpledialog.askstring("Add Empty Frame", "Enter background color (hex code, e.g., #FFFFFF for white):")
        else:
            # Use the size of the existing frames
            frame_size = self.frames[0].size

            # Prompt the user for the background color in hexadecimal format
            color_code = simpledialog.askstring("Add Empty Frame", "Enter background color (hex code, e.g., #FFFFFF for white):")

        # Validate and set the color, default to transparent if invalid
        if color_code and len(color_code) == 7 and color_code[0] == '#':
            try:
                # Test the color code by creating a single pixel image
                Image.new("RGBA", (1, 1), color_code).verify()
            except ValueError:
                messagebox.showerror("Invalid Color", "The entered color code is invalid. Using transparent background instead.")
                color_code = None
        else:
            color_code = None

        self.save_state()  # Save the state before making changes

        # Create a new empty frame with the specified or default color
        try:
            new_frame = Image.new("RGBA", frame_size, color_code if color_code else (0, 0, 0, 0))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create a new frame: {e}")
            return

        # Add the new frame to the list of frames
        self.frames.append(new_frame)
        self.delays.append(100)  # Default delay for new frame
        var = IntVar()
        var.trace_add('write', lambda *args, i=len(self.checkbox_vars): self.set_current_frame(i))
        self.checkbox_vars.append(var)

        self.update_frame_list()
        self.show_frame()

    def delete_frames(self, event=None):
        """Delete the selected frames."""
        if not self.frames:
            messagebox.showerror("Error", "No frames to delete.")
            return

        self.save_state()  # Save the state before making changes
        indices_to_delete = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not indices_to_delete:
            messagebox.showinfo("Info", "No frames selected for deletion.")
            return

        for index in reversed(indices_to_delete):
            del self.frames[index]
            del self.delays[index]
            del self.checkbox_vars[index]

        # Update frame_index to ensure it is within the correct bounds
        if self.frame_index >= len(self.frames):
            self.frame_index = max(0, len(self.frames) - 1)

        self.update_frame_list()
        self.show_frame()  # Update the frame display

    def delete_unchecked_frames(self, event=None):
        """Delete all frames that are not checked in the checkbox list."""
        if not self.frames:
            messagebox.showerror("Error", "No frames to delete.")
            return

        self.save_state()  # Save the state before making changes

        indices_to_keep = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not indices_to_keep:
            messagebox.showinfo("Info", "No frames are checked to keep.")
            return

        # Keep only the checked frames
        self.frames = [self.frames[i] for i in indices_to_keep]
        self.delays = [self.delays[i] for i in indices_to_keep]
        self.checkbox_vars = [self.checkbox_vars[i] for i in indices_to_keep]

        # Update frame_index to ensure it is within the correct bounds
        if self.frame_index >= len(self.frames):
            self.frame_index = max(0, len(self.frames) - 1)

        self.update_frame_list()
        self.show_frame()  # Update the frame display

    def prompt_and_move_selected_frames(self):
        """Prompt the user for the target position and move the selected frames."""
        if not self.frames:
            messagebox.showerror("Error", "No frames available to move.")
            return

        target_position = simpledialog.askinteger("Move Frames", "Enter the target position (0-based index):",
                                                  minvalue=0, maxvalue=len(self.frames) - 1)
        if target_position is not None:
            self.move_selected_frames(target_position)

    def move_selected_frames(self, target_position):
        """
        Move selected frames to a specific target position.

        Parameters:
        - target_position (int): The position where the selected frames should be moved.

        This function moves all the frames with checkboxes checked to the specified target position in a safe and consistent manner.
        """
        if not self.frames:
            messagebox.showerror("Error", "No frames available to move.")
            return

        if target_position < 0 or target_position >= len(self.frames):
            messagebox.showerror("Error", "Invalid target position.")
            return

        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected to move.")
            return

        self.save_state()  # Save the state before making changes

        # Get the selected frames and their delays
        selected_frames = [self.frames[i] for i in selected_indices]
        selected_delays = [self.delays[i] for i in selected_indices]

        # Remove selected frames from their original positions
        for index in reversed(selected_indices):
            del self.frames[index]
            del self.delays[index]
            del self.checkbox_vars[index]

        # Insert selected frames at the target position
        for i, (frame, delay) in enumerate(zip(selected_frames, selected_delays)):
            insert_position = target_position + i
            self.frames.insert(insert_position, frame)
            self.delays.insert(insert_position, delay)
            var = IntVar(value=1)  # Check the checkbox for the moved frames
            var.trace_add('write', lambda *args, i=insert_position: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_position, var)

        self.update_frame_list()
        self.show_frame()

    def move_frame_up(self, event=None):
        """Move the selected frame up in the list."""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one frame to move.")
            return

        selected_index = selected_indices[0]

        if selected_index == 0:
            messagebox.showinfo("Move Up", "The selected frame is already at the top.")
            return

        self.save_state()  # Save the state before making changes

        # Swap the frames and delays
        self.frames[selected_index], self.frames[selected_index - 1] = self.frames[selected_index - 1], self.frames[selected_index]
        self.delays[selected_index], self.delays[selected_index - 1] = self.delays[selected_index - 1], self.delays[selected_index]

        # Move the check state
        self.checkbox_vars[selected_index].set(0)
        self.checkbox_vars[selected_index - 1].set(1)

        # Update the frame index to the new position of the moved frame
        self.frame_index = selected_index - 1

        self.update_frame_list()
        self.show_frame()

    def move_frame_down(self, event=None):
        """Move the selected frame down in the list."""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one frame to move.")
            return

        selected_index = selected_indices[0]

        if selected_index == len(self.frames) - 1:
            messagebox.showinfo("Move Down", "The selected frame is already at the bottom.")
            return

        self.save_state()  # Save the state before making changes

        # Swap the frames and delays
        self.frames[selected_index], self.frames[selected_index + 1] = self.frames[selected_index + 1], self.frames[selected_index]
        self.delays[selected_index], self.delays[selected_index + 1] = self.delays[selected_index + 1], self.delays[selected_index]

        # Move the check state
        self.checkbox_vars[selected_index].set(0)
        self.checkbox_vars[selected_index + 1].set(1)

        # Update the frame index to the new position of the moved frame
        self.frame_index = selected_index + 1

        self.update_frame_list()
        self.show_frame()

    def rotate_selected_frames_180(self):
        """Rotate the selected frames 180 degrees."""
        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = frame.rotate(180)
        self.update_frame_list()
        self.show_frame()
    
    def rotate_selected_frames_90_cw(self):
        """Rotate the selected frames 90 degrees clockwise."""
        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = frame.rotate(-90, expand=True)
        self.update_frame_list()
        self.show_frame()

    def rotate_selected_frames_90_ccw(self):
        """Rotate the selected frames 90 degrees counterclockwise."""
        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = frame.rotate(90, expand=True)
        self.update_frame_list()
        self.show_frame()

    def rotate_selected_frames(self):
        """Rotate the selected frames by a user-specified number of degrees."""
        try:
            angle = simpledialog.askfloat("Rotate Frames", "Enter the rotation angle in degrees:", parent=self.master)
            if angle is None:  # User canceled the dialog
                return

            self.save_state()  # Save the state before making changes

            for i, frame in enumerate(self.frames):
                if self.checkbox_vars[i].get() == 1:
                    self.frames[i] = frame.rotate(angle, expand=True)

            self.update_frame_list()
            self.show_frame()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the rotation angle.")

    def flip_selected_frames_horizontal(self):
        """Flip the selected frames horizontally."""
        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = frame.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_frame_list()
        self.show_frame()

    def flip_selected_frames_vertical(self):
        """Flip the selected frames vertically."""
        self.save_state()  # Save the state before making changes
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = frame.transpose(Image.FLIP_TOP_BOTTOM)
        self.update_frame_list()
        self.show_frame()

    def toggle_check_all(self, event=None):
        """Toggle all checkboxes in the frame list without scrolling or changing the displayed frame."""
        self.save_state()  # Save the state before making changes
        new_state = not self.check_all.get()
        self.check_all.set(new_state)
        
        # Temporarily remove traces
        for var in self.checkbox_vars:
            var.trace_remove('write', var.trace_info()[0][1])
        
        for var in self.checkbox_vars:
            var.set(1 if new_state else 0)
        
        # Re-add traces
        for i, var in enumerate(self.checkbox_vars):
            var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
        
        self.update_frame_list()
    
    def mark_even_odd_frames(self):
        """Mark the checkboxes of all even or odd frames based on user input."""
        self.save_state()  # Save the state before making changes
        choice = simpledialog.askinteger("Select Frames", "Enter 1 to mark odd frames, 2 to mark even frames:")

        if choice not in [1, 2]:
            messagebox.showerror("Invalid Input", "Please enter 1 for odd frames or 2 for even frames.")
            return

        # Clear all checkboxes first
        for var in self.checkbox_vars:
            var.set(0)

        # Mark even or odd frames based on user input
        for i, var in enumerate(self.checkbox_vars):
            if choice == 1 and i % 2 == 0:  # 1 for odd frames (0-based index)
                var.set(1)
            elif choice == 2 and i % 2 != 0:  # 2 for even frames (0-based index)
                var.set(1)

    def mark_frames_relative_to_cursor(self):
        """Mark all frames that are below or above the cursor in the frame list based on user input."""
        direction = simpledialog.askstring("Mark Frames", "Enter 'up' to mark frames above or 'down' to mark frames below the current frame:")

        if direction not in ["up", "down"]:
            messagebox.showerror("Invalid Input", "Please enter 'up' or 'down'.")
            return

        if direction == "up":
            for i in range(self.frame_index + 1):
                self.checkbox_vars[i].set(1)
        elif direction == "down":
            for i in range(self.frame_index, len(self.checkbox_vars)):
                self.checkbox_vars[i].set(1)

        self.update_frame_list()

    def go_to_frame(self):
        """Prompt the user to enter a frame number and go to that frame."""
        if not self.frames:
            messagebox.showerror("Error", "No frames available.")
            return

        frame_number = simpledialog.askinteger("Go to Frame", "Enter frame number:", minvalue=1, maxvalue=len(self.frames))

        if frame_number is not None:
            self.frame_index = frame_number - 1
            self.show_frame()
            self.focus_current_frame()

    def crop_frames(self):
        """Crop the selected frames based on user input values for each side."""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected for cropping.")
            return

        # Prompt user for crop values
        try:
            crop_left = int(simpledialog.askstring("Crop", "Enter pixels to crop from the left:", parent=self.master))
            crop_right = int(simpledialog.askstring("Crop", "Enter pixels to crop from the right:", parent=self.master))
            crop_top = int(simpledialog.askstring("Crop", "Enter pixels to crop from the top:", parent=self.master))
            crop_bottom = int(simpledialog.askstring("Crop", "Enter pixels to crop from the bottom:", parent=self.master))
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", "Please enter valid integers for cropping values.")
            return

        # Validate crop values
        if crop_left < 0 or crop_right < 0 or crop_top < 0 or crop_bottom < 0:
            messagebox.showerror("Invalid Input", "Crop values must be non-negative integers.")
            return

        self.save_state()  # Save the state before making changes

        for index in selected_indices:
            frame = self.frames[index]
            width, height = frame.size
            left = max(0, crop_left)
            top = max(0, crop_top)
            right = width - max(0, crop_right)
            bottom = height - max(0, crop_bottom)

            if right <= left or bottom <= top:
                messagebox.showerror("Invalid Crop Values", "Cropping values are too large.")
                return

            cropped_frame = frame.crop((left, top, right, bottom))
            self.frames[index] = cropped_frame

        self.update_frame_list()
        self.show_frame()

    def resize_frames_dialog(self):
        """Open a simple dialog to get new size and resize all frames."""
        if not any(var.get() for var in self.checkbox_vars):
            messagebox.showinfo("info", "No frames are selected for resizing.")
            return

        width = simpledialog.askinteger("Input", "Enter new width:", parent=self.master, minvalue=1)
        height = simpledialog.askinteger("Input", "Enter new height:", parent=self.master, minvalue=1)
        
        if width and height:
            self.resize_frames(width, height)

    def resize_frames(self, new_width, new_height):
        """Resize all checked frames to the specified width and height."""
        self.save_state()
        for i, frame in enumerate(self.frames):
            if self.checkbox_vars[i].get():
                self.frames[i] = frame.resize((new_width, new_height), Image.LANCZOS)
        self.update_frame_list()
        self.show_frame()

    def copy_frames(self, event=None):
        """Copy the selected frames to the clipboard."""
        self.copied_frames = [(self.frames[i].copy(), self.delays[i]) for i in range(len(self.checkbox_vars)) if self.checkbox_vars[i].get() == 1]
        if not self.copied_frames:
            messagebox.showinfo("Info", "No frames selected to copy.")
        else:
            messagebox.showinfo("Info", f"Copied {len(self.copied_frames)} frame(s).")

    def paste_frames(self, event=None):
        """Paste the copied frames below the selected frames with all checkboxes checked."""
        # Check if there are any frames copied
        if not hasattr(self, 'copied_frames') or not self.copied_frames:
            messagebox.showerror("Error", "No frames to paste. Please copy frames first.")
            return

        # Get the selected indices
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if not selected_indices:
            messagebox.showinfo("Info", "No frames selected to paste after. Pasting at the end.")
            insert_index = len(self.frames)
        else:
            insert_index = max(selected_indices) + 1

        # Save the current state for undo functionality
        self.save_state()

        # Insert the copied frames and delays at the specified index
        for frame, delay in self.copied_frames:
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar(value=1)  # Set the checkbox to be checked by default
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        # Update the frame list and display the current frame
        self.update_frame_list()
        self.show_frame()

    def undo(self, event=None):
        """Undo the last action."""
        if self.history:
            self.redo_stack.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = self.history.pop()
            self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
            for i, var in enumerate(self.checkbox_vars):
                var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
            self.base_size = self.frames[0].size if self.frames else None  # Reset base size based on the remaining frames
            self.update_frame_list()
            self.show_frame()
            self.update_title()
            self.check_all.set(False)  # Reset the check_all variable to ensure consistency

    def redo(self, event=None):
        """Redo the last undone action."""
        if self.redo_stack:
            self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
            self.frames, self.delays, checkbox_states, self.frame_index, self.current_file = self.redo_stack.pop()
            self.checkbox_vars = [IntVar(value=state) for state in checkbox_states]
            for i, var in enumerate(self.checkbox_vars):
                var.trace_add('write', lambda *args, i=i: self.set_current_frame(i))
            self.update_frame_list()
            self.show_frame()
            self.update_title()
            self.check_all.set(False)  # Reset the check_all variable to ensure consistency

    def crossfade_effect(self):
        """Apply crossfade effect between checked frames with user-defined transition frames."""
        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if len(checked_indices) < 2:
            messagebox.showinfo("Info", "Need at least two checked frames to apply crossfade effect.")
            return

        # Ask user for the number of transition frames
        transition_frames_count = simpledialog.askinteger("Crossfade Frames", "Enter the number of transition frames:", parent=self.master)
        if transition_frames_count is None or transition_frames_count < 1:
            messagebox.showerror("Error", "Number of transition frames must be at least 1.")
            return

        self.save_state()  # Save the state before making changes

        crossfade_frames = []
        crossfade_delays = []

        def blend_frames(frame1, frame2, alpha):
            """Blend two frames with given alpha."""
            return Image.blend(frame1, frame2, alpha)

        for idx in range(len(checked_indices) - 1):
            i = checked_indices[idx]
            j = checked_indices[idx + 1]

            frame1 = self.frames[i].convert("RGBA")
            frame2 = self.frames[j].convert("RGBA")
            crossfade_frames.append(frame1)
            crossfade_delays.append(self.delays[i])

            # Generate crossfade frames
            for step in range(1, transition_frames_count + 1):
                alpha = step / float(transition_frames_count + 1)
                blended_frame = blend_frames(frame1, frame2, alpha)
                crossfade_frames.append(blended_frame)
                crossfade_delays.append(self.delays[i] // (transition_frames_count + 1))

        # Insert crossfade frames and delays at the correct positions
        for idx in range(len(checked_indices) - 1, -1, -1):
            i = checked_indices[idx]
            self.frames.pop(i)
            self.delays.pop(i)
            self.checkbox_vars.pop(i)

        insert_index = checked_indices[0]
        for frame, delay in zip(crossfade_frames, crossfade_delays):
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar(value=1)
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        self.update_frame_list()
        self.show_frame()

    def reverse_frames(self):
        """Apply reverse effect to the selected frames."""
        self.save_state()  # Save the state before making changes
        indices_to_reverse = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        
        if not indices_to_reverse:
            messagebox.showinfo("Info", "No frames selected for reversing.")
            return

        # Extract the selected frames and their delays
        frames_to_reverse = [self.frames[i] for i in indices_to_reverse]
        delays_to_reverse = [self.delays[i] for i in indices_to_reverse]

        # Reverse the selected frames and their delays
        frames_to_reverse.reverse()
        delays_to_reverse.reverse()

        # Replace the selected frames and their delays with the reversed versions
        for idx, i in enumerate(indices_to_reverse):
            self.frames[i] = frames_to_reverse[idx]
            self.delays[i] = delays_to_reverse[idx]

        self.show_frame()
        self.update_frame_list()

    def desaturate_frames(self):
        """Apply desaturation effect to the selected frames."""
        self.save_state()  # Save the state before making changes
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                self.frames[i] = frame.convert("L").convert("RGBA")  # Convert to grayscale and then back to RGBA
        self.show_frame()
        self.update_frame_list()

    def apply_sharpening_effect(self):
        """Apply a sharpening effect to the selected frames with user-defined intensity."""
        # Prompt the user for the sharpening intensity
        sharpening_intensity = simpledialog.askfloat(
            "Sharpening Effect", 
            "Enter sharpening intensity (e.g., 9.0 for 900%):", 
            minvalue=1.0
        )
        
        if sharpening_intensity is None:
            return  # User canceled the dialog

        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                # Apply the sharpening filter with the user-defined intensity
                enhancer = ImageEnhance.Sharpness(frame)
                self.frames[i] = enhancer.enhance(sharpening_intensity)
        
        self.update_frame_list()
        self.show_frame()

    
    def apply_strange_sharpening_effect(self):
        """Apply a specialized sharpening effect to the selected frames for ghost and UFO photo studies."""
        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                # Convert to grayscale to highlight edges more effectively
                gray_frame = frame.convert("L")
                
                # Apply a strong edge enhancement filter
                edge_enhanced = gray_frame.filter(ImageFilter.EDGE_ENHANCE_MORE)
                
                # Sharpen the image dramatically
                sharpener = ImageEnhance.Sharpness(edge_enhanced)
                sharpened_frame = sharpener.enhance(10.0)  # Increase sharpness significantly

                # Optionally, enhance contrast to make features stand out more
                contrast_enhancer = ImageEnhance.Contrast(sharpened_frame)
                enhanced_frame = contrast_enhancer.enhance(2.0)  # Increase contrast

                # Convert back to RGBA (if needed)
                self.frames[i] = enhanced_frame.convert("RGBA")
        
        self.update_frame_list()
        self.show_frame()

    def ghost_detection_effect(self):
        """Apply a ghost detection effect to the selected frames."""
        from PIL import ImageEnhance, ImageOps, ImageFilter, ImageChops

        # Function to enhance and apply a ghostly effect
        def apply_ghost_effect(frame):
            # Convert to grayscale
            gray_frame = frame.convert("L")

            # Enhance contrast using histogram equalization
            equalized_frame = ImageOps.equalize(gray_frame)

            # Apply Gaussian blur to reduce noise
            blurred_frame = equalized_frame.filter(ImageFilter.GaussianBlur(2))

            # Use adaptive thresholding to create a binary image
            threshold_frame = blurred_frame.point(lambda p: p > 128 and 255)

            # Apply edge detection (using Canny edge detector if possible)
            edges = threshold_frame.filter(ImageFilter.FIND_EDGES)

            # Enhance edges to make them more prominent
            enhancer = ImageEnhance.Contrast(edges)
            enhanced_edges = enhancer.enhance(2.0)

            # Invert the image to create a ghostly effect
            inverted_image = ImageOps.invert(enhanced_edges)

            # Convert back to RGBA
            ghost_frame = inverted_image.convert("RGBA")

            # Blend the original frame with the ghost frame to create a more realistic apparition
            blended_frame = Image.blend(frame.convert("RGBA"), ghost_frame, alpha=0.5)

            return blended_frame

        # Apply the ghost effect to selected frames
        self.save_state()  # Save the state before making changes
        for i in range(len(self.frames)):
            if self.checkbox_vars[i].get() == 1:
                self.frames[i] = apply_ghost_effect(self.frames[i])

            self.show_frame()
            self.update_frame_list()
        
    def invert_colors_of_selected_frames(self):
        """Invert colors of the selected frames."""
        if not any(var.get() for var in self.checkbox_vars):
            messagebox.showinfo("Info", "No frames selected for color inversion.")
            return

        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                self.frames[i] = ImageOps.invert(self.frames[i].convert("RGB")).convert("RGBA")
        
        self.update_frame_list()
        self.show_frame()

    def apply_tint(self):
            """Apply a tint effect to the selected frames."""
            # Prompt user for hex color code and intensity
            color_code = simpledialog.askstring("Tint Effect", "Enter tint color (hex code, e.g., #FF0000 for red):")
            if not color_code or not (color_code.startswith('#') and len(color_code) == 7):
                messagebox.showerror("Invalid Input", "Please enter a valid hex color code (e.g., #FF0000).")
                return
            
            intensity = simpledialog.askinteger("Tint Effect", "Enter intensity (0-100):", minvalue=0, maxvalue=100)
            if intensity is None or not (0 <= intensity <= 100):
                messagebox.showerror("Invalid Input", "Please enter an intensity value between 0 and 100.")
                return

            self.save_state()  # Save the state before making changes

            # Apply the tint effect to the selected frames
            for i, var in enumerate(self.checkbox_vars):
                if var.get() == 1:
                    self.frames[i] = self.tint_image(self.frames[i], color_code, intensity)
            
            self.show_frame()
            self.update_frame_list()

    def tint_image(self, image, color_code, intensity):
        """Tint an image with the given color and intensity."""
        r, g, b = Image.new("RGB", (1, 1), color_code).getpixel((0, 0))
        intensity /= 100.0

        # Create a tinted image
        tinted_image = Image.new("RGBA", image.size)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.getpixel((x, y))
                tr = int(pixel[0] + (r - pixel[0]) * intensity)
                tg = int(pixel[1] + (g - pixel[1]) * intensity)
                tb = int(pixel[2] + (b - pixel[2]) * intensity)
                ta = pixel[3]
                tinted_image.putpixel((x, y), (tr, tg, tb, ta))

        return tinted_image

    def apply_random_glitch_effect(self):
        """Apply a random glitch effect to the selected frames."""
        def glitch_frame(frame):
            """Apply glitch effect to a single frame."""
            width, height = frame.size

            # Convert frame to RGB
            frame = frame.convert("RGB")
            r, g, b = frame.split()

            # Randomly offset each color channel (Chromatic Aberration)
            r = r.transform(r.size, Image.AFFINE, (1, 0, random.uniform(-3, 3), 0, 1, random.uniform(-3, 3)))
            g = g.transform(g.size, Image.AFFINE, (1, 0, random.uniform(-3, 3), 0, 1, random.uniform(-3, 3)))
            b = b.transform(b.size, Image.AFFINE, (1, 0, random.uniform(-3, 3), 0, 1, random.uniform(-3, 3)))

            # Merge channels back
            frame = Image.merge("RGB", (r, g, b))

            # Add displacement mapping
            displacement = Image.effect_noise((width, height), 100)
            displacement = displacement.filter(ImageFilter.GaussianBlur(1))
            displacement = displacement.point(lambda p: p > 128 and 255)
            frame = Image.composite(frame, frame.filter(ImageFilter.GaussianBlur(5)), displacement)

            # Convert back to RGBA
            frame = frame.convert("RGBA")

            # Add random noise
            pixels = frame.load()
            for _ in range(random.randint(1000, 3000)):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                noise = random.randint(50, 200)  # Gray noise
                pixels[x, y] = (noise, noise, noise, pixels[x, y][3])

            # Add horizontal gray lines with grain
            for _ in range(random.randint(5, 20)):
                y = random.randint(0, height - 1)
                line_height = random.randint(1, 3)
                gray_value = random.randint(50, 200)  # Gray line color
                for line in range(line_height):
                    if y + line < height:
                        for x in range(width):
                            grain = random.randint(-20, 20)  # Add grain effect
                            alpha = pixels[x, y + line][3]
                            gray_with_grain = min(max(gray_value + grain, 0), 255)
                            pixels[x, y + line] = (gray_with_grain, gray_with_grain, gray_with_grain, alpha)

            return frame

        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                glitched_frame = glitch_frame(frame.copy())
                self.frames[i] = glitched_frame

        self.update_frame_list()
        self.show_frame()

    def apply_sketch_effect(self):
        """Apply a sketch effect to the selected frames."""
        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i].convert("L")  # Convert to grayscale
                inverted_frame = ImageOps.invert(frame)  # Invert colors
                blurred_frame = inverted_frame.filter(ImageFilter.GaussianBlur(10))  # Apply Gaussian blur
                sketch_frame = Image.blend(frame, blurred_frame, 0.5).convert("RGBA")  # Blend the original and blurred frames
                
                # Enhance edges
                edge_enhanced_frame = sketch_frame.filter(ImageFilter.EDGE_ENHANCE_MORE)
                self.frames[i] = edge_enhanced_frame

        self.update_frame_list()
        self.show_frame()

    def prompt_and_apply_brightness_contrast(self):
        """Prompt the user for brightness and contrast levels, then apply the changes to selected frames."""
        brightness = simpledialog.askfloat("Brightness", "Enter brightness level (e.g., 1.0 for no change):", minvalue=0.0)
        contrast = simpledialog.askfloat("Contrast", "Enter contrast level (e.g., 1.0 for no change):", minvalue=0.0)
        
        if brightness is not None and contrast is not None:
            self.apply_brightness_contrast(brightness, contrast)

    def apply_brightness_contrast(self, brightness=1.0, contrast=1.0):
        """Apply brightness and contrast adjustments to selected frames.
        
        Parameters:
        - brightness (float): Brightness factor, where 1.0 means no change, less than 1.0 darkens the image,
          and greater than 1.0 brightens the image.
        - contrast (float): Contrast factor, where 1.0 means no change, less than 1.0 reduces contrast,
          and greater than 1.0 increases contrast.
        """
        # Save the state before making changes
        self.save_state()

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                # Apply brightness adjustment
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(brightness)
                # Apply contrast adjustment
                enhancer = ImageEnhance.Contrast(frame)
                frame = enhancer.enhance(contrast)
                self.frames[i] = frame

        # Update the frame list and show the current frame
        self.update_frame_list()
        self.show_frame()

    def adjust_hsl(self):
        """Prompt the user for Hue, Saturation, and Lightness adjustments and apply them to selected frames."""
        # Get user input for HSL adjustments
        hue_shift = simpledialog.askfloat("Adjust Hue", "Enter hue shift (-180 to 180):", minvalue=-180, maxvalue=180)
        if hue_shift is None:
            return
        saturation_factor = simpledialog.askfloat("Adjust Saturation", "Enter saturation factor (0.0 to 2.0):", minvalue=0.0, maxvalue=2.0)
        if saturation_factor is None:
            return
        lightness_factor = simpledialog.askfloat("Adjust Lightness", "Enter lightness factor (0.0 to 2.0):", minvalue=0.0, maxvalue=2.0)
        if lightness_factor is None:
            return

        self.save_state()  # Save the state before making changes

        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i].convert("RGB")

                # Adjust Hue
                hsv_image = frame.convert("HSV")
                hsv_data = list(hsv_image.getdata())
                hsv_data = [(int((h + hue_shift) % 360), s, v) for h, s, v in hsv_data]
                hsv_image.putdata(hsv_data)
                frame = hsv_image.convert("RGB")

                # Adjust Saturation
                enhancer = ImageEnhance.Color(frame)
                frame = enhancer.enhance(saturation_factor)

                # Adjust Lightness
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(lightness_factor)

                self.frames[i] = frame.convert("RGBA")

        self.update_frame_list()
        self.show_frame()

    def apply_zoom_effect(self):
        """Apply a zoom effect to the selected frames."""
        # Prompt the user for the zoom intensity
        zoom_factor = simpledialog.askfloat("Zoom Effect", "Enter zoom intensity (e.g., 1.2 for 20% zoom in):", minvalue=0.1)
        if zoom_factor is None:
            return

        # Save the state before making changes for undo functionality
        self.save_state()

        # Apply zoom effect to each selected frame
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                width, height = frame.size
                new_width = int(width * zoom_factor)
                new_height = int(height * zoom_factor)
                zoomed_frame = frame.resize((new_width, new_height), Image.LANCZOS)

                # Center crop the zoomed frame to the original size
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                right = left + width
                bottom = top + height
                self.frames[i] = zoomed_frame.crop((left, top, right, bottom))

        # Update the frame list and show the current frame
        self.update_frame_list()
        self.show_frame()

    def apply_zoom_effect_click(self):
        """Apply a zoom effect to the selected frames."""
        zoom_factor = simpledialog.askfloat("Zoom Effect", "Enter zoom factor (e.g., 2 for 200% zoom in, 0.5 for 50% zoom out):", minvalue=0.1)
        if zoom_factor is None:
            return

        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if not checked_indices:
            messagebox.showinfo("Zoom Effect", "No frames selected for zooming.")
            return

        self.save_state()  # Save the state before making changes

        zoom_applied = False

        def on_click(event, preview_width, preview_height):
            nonlocal zoom_applied
            """Zoom into or out of the image at the clicked position."""
            for frame_index in checked_indices:
                frame = self.frames[frame_index]
                width, height = frame.size
                click_x = event.x * (width / preview_width)
                click_y = event.y * (height / preview_height)

                new_width = int(width * zoom_factor)
                new_height = int(height * zoom_factor)
                zoomed_frame = frame.resize((new_width, new_height), Image.LANCZOS)

                if zoom_factor > 1:
                    left = max(0, min(int(click_x * zoom_factor - width // 2), new_width - width))
                    top = max(0, min(int(click_y * zoom_factor - height // 2), new_height - height))
                    right = left + width
                    bottom = top + height
                    self.frames[frame_index] = zoomed_frame.crop((left, top, right, bottom))
                else:
                    left = max(0, min(int(click_x - new_width // 2), width - new_width))
                    top = max(0, min(int(click_y - new_height // 2), height - new_height))
                    right = left + new_width
                    bottom = top + new_height

                    # Create a new image with the original size and paste the zoomed-out image onto it
                    new_frame = Image.new("RGBA", (width, height))
                    new_frame.paste(zoomed_frame, (left, top))
                    self.frames[frame_index] = new_frame

            zoom_applied = True
            zoom_window.destroy()
            self.update_frame_list()
            self.show_frame()

        # Create a new window to display the image
        zoom_window = tk.Toplevel(self.master)
        zoom_window.title("Click to Zoom")

        zoom_canvas = tk.Canvas(zoom_window)
        zoom_canvas.pack()

        def display_preview(frame):
            """Display the preview of the frame in the zoom window."""
            preview = self.resize_image(frame, max_width=self.preview_width, max_height=self.preview_height)
            preview_width, preview_height = preview.size
            photo = ImageTk.PhotoImage(preview)
            zoom_canvas.config(width=preview_width, height=preview_height)
            zoom_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            zoom_canvas.image = photo  # Keep a reference to avoid garbage collection
            zoom_canvas.bind("<Button-1>", lambda event: on_click(event, preview_width, preview_height))

        display_preview(self.frames[checked_indices[0]])

        def on_close():
            zoom_window.destroy()

        zoom_window.protocol("WM_DELETE_WINDOW", on_close)

        zoom_window.mainloop()

    def apply_blur_effect(self):
        """Apply blur effect to selected frames with user-defined intensity."""
        # Prompt user for blur intensity
        blur_intensity = simpledialog.askinteger("Blur Effect", "Enter blur intensity (e.g., 2 for slight blur):", minvalue=0)
        if blur_intensity is None or blur_intensity < 0:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for blur intensity.")
            return

        self.save_state()  # Save the state before making changes

        # Apply the blur effect to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                self.frames[i] = self.frames[i].filter(ImageFilter.GaussianBlur(blur_intensity))

        self.update_frame_list()
        self.show_frame()

    def apply_zoom_and_speed_blur_effect(self):
        """Prompt user to apply a zoom or speed blur effect to selected frames."""
        # Check if there is at least one frame selected
        if not any(var.get() for var in self.checkbox_vars):
            messagebox.showinfo("Info", "No frames selected for applying the effect.")
            return

        # Prompt user for effect type
        effect_type = simpledialog.askstring("Choose Effect", "Enter effect type (zoom or speed):")
        if effect_type is None:
            return  # User cancelled
        effect_type = effect_type.strip().lower()
        if effect_type not in ["zoom", "speed"]:
            messagebox.showerror("Invalid Input", "Please enter a valid effect type: 'zoom' or 'speed'.")
            return

        # Prompt user for intensity
        intensity = simpledialog.askfloat("Effect Intensity", "Enter intensity (e.g., 1.2 for zoom, 5 for speed):", minvalue=0.1)
        if intensity is None:
            return  # User cancelled

        # Handle speed blur specific input
        if effect_type == "speed":
            direction = simpledialog.askstring("Speed Blur Direction", "Enter direction (right, left, top, bottom):")
            if direction is None:
                return  # User cancelled
            direction = direction.strip().lower()
            if direction not in ["right", "left", "top", "bottom"]:
                messagebox.showerror("Invalid Input", "Please enter a valid direction: 'right', 'left', 'top', 'bottom'.")
                return

        self.save_state()  # Save the state before making changes

        # Apply the chosen effect to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                if effect_type == "zoom":
                    self.frames[i] = self.apply_zoom_blur(self.frames[i], intensity)
                elif effect_type == "speed":
                    self.frames[i] = self.apply_speed_blur(self.frames[i], intensity, direction)

        self.update_frame_list()
        self.show_frame()

    def apply_zoom_blur(self, frame, intensity):
        """Apply a zoom blur effect to a frame."""
        width, height = frame.size

        zoomed_frame = frame.copy()
        for i in range(1, int(intensity * 10) + 1):
            zoom_factor = 1 + i * 0.01
            layer = frame.resize((int(width * zoom_factor), int(height * zoom_factor)), Image.LANCZOS)
            layer = layer.crop((
                (layer.width - width) // 2,
                (layer.height - height) // 2,
                (layer.width + width) // 2,
                (layer.height + height) // 2
            ))
            zoomed_frame = Image.blend(zoomed_frame, layer, alpha=0.05)

        return zoomed_frame

    def apply_speed_blur(self, frame, intensity, direction):
        """Apply a speed blur effect to a frame in the specified direction."""
        width, height = frame.size

        speed_blur_frame = frame.copy()
        for i in range(1, int(intensity * 10) + 1):
            offset = int(i * 2)
            if direction == "right":
                matrix = (1, 0, -offset, 0, 1, 0)
            elif direction == "left":
                matrix = (1, 0, offset, 0, 1, 0)
            elif direction == "top":
                matrix = (1, 0, 0, 0, 1, offset)
            elif direction == "bottom":
                matrix = (1, 0, 0, 0, 1, -offset)
            layer = frame.transform(
                frame.size,
                Image.AFFINE,
                matrix,
                resample=Image.BICUBIC
            )
            speed_blur_frame = Image.blend(speed_blur_frame, layer, alpha=0.05)

        return speed_blur_frame

    def apply_noise_effect(self):
        """Apply a noise effect to the selected frames based on user-defined intensity."""
        # Prompt the user for the noise intensity
        intensity = simpledialog.askinteger("Noise Effect", "Enter noise intensity (e.g., 10 for slight noise, 100 for heavy noise):", minvalue=1)
        if intensity is None or intensity < 1:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for noise intensity.")
            return

        self.save_state()  # Save the state before making changes

        def add_noise(image, intensity):
            """Add noise to an image."""
            width, height = image.size
            pixels = image.load()

            for _ in range(width * height * intensity // 100):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                r, g, b, a = pixels[x, y]
                noise = random.randint(-intensity, intensity)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                    a
                )

            return image

        # Apply the noise effect to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i].convert("RGBA")
                self.frames[i] = add_noise(frame, intensity)

        self.update_frame_list()
        self.show_frame()

    def apply_pixelate_effect(self):
        """Apply pixelate effect to selected frames with user-defined intensity."""
        # Prompt user for pixelation intensity
        pixel_size = simpledialog.askinteger("Pixelate Effect", "Enter pixel size (e.g., 10 for blocky effect):", minvalue=1)
        if pixel_size is None or pixel_size < 1:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for pixel size.")
            return

        self.save_state()  # Save the state before making changes

        # Apply the pixelate effect to the selected frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i]
                width, height = frame.size
                # Resize down to pixel size and back up to original size
                small_frame = frame.resize((width // pixel_size, height // pixel_size), Image.NEAREST)
                pixelated_frame = small_frame.resize(frame.size, Image.NEAREST)
                self.frames[i] = pixelated_frame

        self.update_frame_list()
        self.show_frame()

    def reduce_transparency_of_checked_frames(self):
        """Reduce the transparency of the checked frames based on user-defined intensity."""
        # Prompt the user for the transparency reduction intensity
        intensity = simpledialog.askfloat("Transparency Reduction", "Enter intensity (0 to 1):", minvalue=0.0, maxvalue=1.0)
        
        if intensity is None:
            return  # User canceled the dialog

        self.save_state()  # Save the state before making changes

        # Apply the transparency reduction to the checked frames
        for i, var in enumerate(self.checkbox_vars):
            if var.get() == 1:
                frame = self.frames[i].convert("RGBA")
                # Adjust the alpha channel based on the intensity
                alpha = frame.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(intensity)
                frame.putalpha(alpha)
                self.frames[i] = frame

        self.update_frame_list()
        self.show_frame()

    def slide_transition_effect(self):
        """Apply a slide transition effect to the selected frames based on user input for direction and speed."""
        # Check if there are frames with a checked box
        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]
        if len(checked_indices) < 2:
            messagebox.showinfo("Info", "Need at least two checked frames to apply slide transition effect.")
            return

        # Prompt the user for the direction of the slide
        direction = simpledialog.askstring("Slide Transition Effect", "Enter direction (right, top, left, bottom):")
        if direction is None:
            return  # User cancelled
        direction = direction.strip().lower()
        if direction not in ["right", "top", "left", "bottom"]:
            messagebox.showerror("Invalid Input", "Please enter a valid direction: right, top, left, bottom.")
            return

        # Prompt the user for the speed (intensity) of the slide effect
        speed = simpledialog.askinteger("Slide Transition Effect", "Enter speed (number of transition frames, e.g., 10):", minvalue=1)
        if speed is None or speed < 1:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for speed.")
            return

        self.save_state()  # Save the state before making changes

        slide_frames = []
        slide_delays = []

        def generate_slide_frames(frame1, frame2, direction, speed):
            """Generate slide frames transitioning from frame1 to frame2."""
            frames = []
            width, height = frame1.size

            for step in range(speed):
                new_frame = Image.new("RGBA", (width, height))
                offset = int((step + 1) * (width if direction in ["left", "right"] else height) / speed)
                if direction == "right":
                    new_frame.paste(frame2, (-offset, 0))
                    new_frame.paste(frame1, (width - offset, 0))
                elif direction == "left":
                    new_frame.paste(frame2, (offset, 0))
                    new_frame.paste(frame1, (-width + offset, 0))
                elif direction == "top":
                    new_frame.paste(frame2, (0, offset))
                    new_frame.paste(frame1, (0, -height + offset))
                elif direction == "bottom":
                    new_frame.paste(frame2, (0, -offset))
                    new_frame.paste(frame1, (0, height - offset))
                frames.append(new_frame)
            
            return frames

        for idx in range(len(checked_indices) - 1):
            i = checked_indices[idx]
            j = checked_indices[idx + 1]

            frame1 = self.frames[i].convert("RGBA")
            frame2 = self.frames[j].convert("RGBA")
            slide_frames.append(frame1)
            slide_delays.append(self.delays[i])

            generated_frames = generate_slide_frames(frame1, frame2, direction, speed)
            slide_frames.extend(generated_frames)
            slide_delays.extend([self.delays[i] // speed] * speed)

        slide_frames.append(self.frames[checked_indices[-1]])
        slide_delays.append(self.delays[checked_indices[-1]])

        # Remove checked frames in reverse order to maintain correct indices
        for idx in reversed(checked_indices):
            self.frames.pop(idx)
            self.delays.pop(idx)
            self.checkbox_vars.pop(idx)

        # Insert the slide frames in the correct order
        insert_index = checked_indices[0]
        for frame, delay in zip(slide_frames, slide_delays):
            self.frames.insert(insert_index, frame)
            self.delays.insert(insert_index, delay)
            var = IntVar(value=1)
            var.trace_add('write', lambda *args, i=insert_index: self.set_current_frame(i))
            self.checkbox_vars.insert(insert_index, var)
            insert_index += 1

        self.update_frame_list()
        self.show_frame()

    def toggle_play_pause(self, event=None):
        """Toggle play/pause for the animation."""
        if self.is_playing:
            self.stop_animation()
        else:
            self.play_animation()

    def play_animation(self):
        """Play the GIF animation."""
        self.is_playing = True
        self.play_button.config(text="Stop")
        self.play_next_frame()

    def stop_animation(self):
        """Stop the GIF animation."""
        self.is_playing = False
        self.play_button.config(text="Play")

    def change_preview_resolution(self):
        """Change the preview resolution based on user input."""
        MAX_WIDTH = 2560
        MAX_HEIGHT = 1600

        resolution = simpledialog.askstring("Change Preview Resolution", "Enter new resolution (e.g., 800x600):")
        if resolution:
            try:
                width, height = map(int, resolution.split('x'))
                if width > 0 and height > 0:
                    if width <= MAX_WIDTH and height <= MAX_HEIGHT:
                        self.preview_width = width
                        self.preview_height = height
                        self.show_frame()  # Update the displayed frame with new resolution
                    else:
                        messagebox.showerror("Invalid Resolution", f"Resolution exceeds the maximum allowed size of {MAX_WIDTH}x{MAX_HEIGHT}.")
                else:
                    messagebox.showerror("Invalid Resolution", "Width and height must be positive integers.")
            except ValueError:
                messagebox.showerror("Invalid Format", "Please enter the resolution in the format '800x600'.")

    def toggle_transparent_frames_preview(self, event=None):
        """Toggle transparent preview for frames with checked checkboxes."""
        if self.is_preview_mode:
            self.exit_preview_mode()
        else:
            self.enter_preview_mode()

    def enter_preview_mode(self):
        """Enter the transparent preview mode."""
        self.is_preview_mode = True

        if not self.frames:
            messagebox.showinfo("Preview Mode", "No frames available for preview.")
            self.is_preview_mode = False
            return

        checked_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get() == 1]

        if not checked_indices:
            messagebox.showinfo("Preview Mode", "No frames are checked for preview.")
            self.is_preview_mode = False
            return

        if checked_indices[0] >= len(self.frames):
            messagebox.showerror("Error", "Checked frame index is out of range.")
            self.is_preview_mode = False
            return

        composite_frame = Image.new("RGBA", self.frames[0].size, (255, 255, 255, 0))
        transparency_factor = 0.5  # Adjust transparency factor as needed

        for idx, i in enumerate(checked_indices):
            if i >= len(self.frames):
                continue  # Skip if index is out of range

            frame = self.frames[i].copy()
            if idx != 0:  # Only make frames transparent and black and white if not the first checked frame
                frame = frame.convert("L").convert("RGBA")  # Convert to black and white
                alpha = frame.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(transparency_factor)
                frame.putalpha(alpha)
            composite_frame = Image.alpha_composite(composite_frame, frame)

        draw = ImageDraw.Draw(composite_frame)
        font_size = 20
        try:
            font = ImageFont.truetype("arial.ttf", font_size)  # Ensure you have a font file available
        except IOError:
            font = ImageFont.load_default()  # Fall back to default font if specified font is not available
        text = "T"
        text_position = (composite_frame.width - font_size - 20, 10)
        text_color = (255, 0, 0, 255)  # Red color for visibility
        draw.text(text_position, text, font=font, fill=text_color)

        preview = self.resize_image(composite_frame, max_width=self.preview_width, max_height=self.preview_height)
        photo = ImageTk.PhotoImage(preview)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.master.bind_all("<Key>", self.exit_preview_mode)

    def exit_preview_mode(self, event=None):
        """Exit the preview mode and return to normal mode."""
        if self.is_preview_mode:
            self.is_preview_mode = False
            self.show_frame()
            # Unbind the key event
            self.master.unbind_all("<Key>")

    def play_next_frame(self):
        """Play the next frame in the animation."""
        if self.is_playing and self.frames:
            self.show_frame()
            delay = self.delays[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.master.after(delay, self.play_next_frame)
            
    def toggle_draw_mode(self, event=None):
        """Toggle draw mode on and off."""
        self.save_state()  # Save the state before making changes

        # Check if any checkbox is marked
        if not any(var.get() for var in self.checkbox_vars):
            messagebox.showwarning("Draw Mode", "No frame is selected for drawing.")
            self.is_draw_mode = False
            return

        self.is_draw_mode = not self.is_draw_mode
        if self.is_draw_mode:
            # Ensure the current frame is marked
            if not self.checkbox_vars[self.frame_index].get():
                messagebox.showwarning("Draw Mode", "Current frame must be selected for drawing.")
                self.is_draw_mode = False
                return

            # Bind events for drawing and tool selection
            self.master.bind("<Motion>", self.draw)
            self.master.bind("<Button-1>", self.start_drawing)
            self.master.bind("<ButtonRelease-1>", self.stop_drawing)
            self.master.bind("<Key-1>", self.set_tool_brush)
            self.master.bind("<Key-2>", self.set_tool_eraser)
            self.master.bind("<Key-3>", self.set_tool_color)
            self.master.bind("<Key-4>", self.prompt_brush_size)
            self.master.bind("<bracketleft>", self.decrease_brush_size)
            self.master.bind("<bracketright>", self.increase_brush_size)

            self.show_frame_with_overlay()  # Show frame with 'D' overlay
            messagebox.showinfo("Draw Mode", "Entered Draw Mode")
        else:
            # Unbind events when exiting draw mode
            self.master.unbind("<Motion>")
            self.master.unbind("<Button-1>")
            self.master.unbind("<ButtonRelease-1>")
            self.master.unbind("<Key-1>")
            self.master.unbind("<Key-2>")
            self.master.unbind("<Key-3>")
            self.master.unbind("<Key-4>")
            self.master.unbind("<bracketleft>")
            self.master.unbind("<bracketright>")

            self.show_frame()  # Show frame without overlay
            messagebox.showinfo("Draw Mode", "Exited Draw Mode")

    def show_frame_with_overlay(self):
        """Display the current frame with 'D' overlay in the upper right corner."""
        if self.frames:
            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1  # Ensure the frame index is within bounds
            frame = self.frames[self.frame_index]
            preview = self.resize_image(frame, max_width=self.preview_width, max_height=self.preview_height)
            
            # Add 'D' overlay to the preview
            draw = ImageDraw.Draw(preview)
            text_position = (preview.width - 20, 10)
            text_color = (255, 0, 0, 255)  # Red color for visibility
            draw.text(text_position, "D", fill=text_color)
            
            photo = ImageTk.PhotoImage(preview)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.image_label.config(text='')  # Remove text when showing image
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, str(self.delays[self.frame_index]))
            self.dimension_label.config(text=f"Size: {frame.width}x{frame.height}")  # Show frame dimensions
            total_duration = sum(self.delays)
            self.total_duration_label.config(text=f"Total Duration: {total_duration} ms")  # Show total duration
        else:
            self.image_label.config(image='', text="No frames to display")
            self.image_label.image = None
            self.delay_entry.delete(0, tk.END)
            self.dimension_label.config(text="")  # Clear frame dimensions
            self.total_duration_label.config(text="")  # Clear total duration
        self.update_frame_list()  # Refresh the frame list to show the current frame indicator

    def set_tool_brush(self, event=None):
        """Set the drawing tool to brush and display an infobox."""
        self.set_tool('brush')
        messagebox.showinfo("Tool Selected", "Selected Tool: Brush")

    def set_tool_eraser(self, event=None):
        """Set the drawing tool to eraser and display an infobox."""
        self.set_tool('eraser')
        messagebox.showinfo("Tool Selected", "Selected Tool: Eraser")

    def set_tool_color(self, event=None):
        """Open color chooser, set brush color, and display an infobox."""
        self.choose_color()
        messagebox.showinfo("Tool Selected", "Selected Tool: Color")

    def prompt_brush_size(self, event=None):
        """Prompt the user to enter the brush size."""
        size = simpledialog.askinteger("Brush Size", "Enter the brush size:", initialvalue=self.brush_size, minvalue=1)
        if size:
            self.brush_size = size
            messagebox.showinfo("Brush Size", f"Brush size set to: {self.brush_size}")

    def decrease_brush_size(self, event=None):
        """Decrease the brush size and display the new size in an infobox."""
        self.change_brush_size(-1)
        messagebox.showinfo("Brush Size", f"Brush size changed to: {self.brush_size}")

    def increase_brush_size(self, event=None):
        """Increase the brush size and display the new size in an infobox."""
        self.change_brush_size(1)
        messagebox.showinfo("Brush Size", f"Brush size changed to: {self.brush_size}")

    def set_tool(self, tool):
        """Set the current drawing tool."""
        self.tool = tool

    def choose_color(self):
        """Open a color chooser dialog to select the brush color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.brush_color = color

    def change_brush_size(self, delta):
        """Change the brush size."""
        new_size = self.brush_size + delta
        if new_size > 0:
            self.brush_size = new_size

    def start_drawing(self, event):
        """Start drawing on the canvas."""
        self.is_drawing = True
        self.last_x, self.last_y = self.scale_coordinates(event.x, event.y)

    def stop_drawing(self, event):
        """Stop drawing on the canvas."""
        self.is_drawing = False

    def draw(self, event):
        """Draw on the canvas."""
        if self.is_draw_mode and self.is_drawing:
            x, y = self.scale_coordinates(event.x, event.y)
            if self.checkbox_vars[self.frame_index].get() == 1:
                frame = self.frames[self.frame_index].copy()
                draw = ImageDraw.Draw(frame)
                if self.tool == 'brush':
                    self.draw_brush(draw, self.last_x, self.last_y, x, y)
                elif self.tool == 'eraser':
                    draw.line([self.last_x, self.last_y, x, y], fill=(255, 255, 255, 0), width=self.brush_size)
                self.frames[self.frame_index] = frame
                self.last_x, self.last_y = x, y
                self.show_frame_with_overlay()  # Ensure 'D' overlay remains after drawing


    def draw_brush(self, draw, x1, y1, x2, y2):
        """Draw a smooth, round brush stroke."""
        # Increase the exponent to 0.9 for a smoother line with more steps
        distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.9
        num_steps = int(distance / self.brush_size) + 1
        for i in range(num_steps):
            x = x1 + i * (x2 - x1) / num_steps
            y = y1 + i * (y2 - y1) / num_steps
            draw.ellipse([x - self.brush_size / 2, y - self.brush_size / 2, x + self.brush_size / 2, y + self.brush_size / 2], fill=self.brush_color, outline=self.brush_color)


    def scale_coordinates(self, x, y):
        """Scale the coordinates based on the current preview resolution."""
        original_width, original_height = self.frames[self.frame_index].size
        scale_x = original_width / self.preview_width
        scale_y = original_height / self.preview_height
        return int(x * scale_x), int(y * scale_y)

    def change_preview_resolution(self):
        """Change the preview resolution based on user input."""
        MAX_WIDTH = 2560
        MAX_HEIGHT = 1600

        resolution = simpledialog.askstring("Change Preview Resolution", "Enter new resolution (e.g., 800x600):")
        if resolution:
            try:
                width, height = map(int, resolution.split('x'))
                if width > 0 and height > 0:
                    if width <= MAX_WIDTH and height <= MAX_HEIGHT:
                        self.preview_width = width
                        self.preview_height = height
                        self.show_frame()  # Update the displayed frame with new resolution
                    else:
                        messagebox.showerror("Invalid Resolution", f"Resolution exceeds the maximum allowed size of {MAX_WIDTH}x{MAX_HEIGHT}.")
                else:
                    messagebox.showerror("Invalid Resolution", "Width and height must be positive integers.")
            except ValueError:
                messagebox.showerror("Invalid Format", "Please enter the resolution in the format '800x600'.")

    def set_delay(self, event=None):
        """Set the delay for the selected frames."""
        try:
            delay = int(self.delay_entry.get())
            self.save_state()  # Save the state before making changes
            for i, var in enumerate(self.checkbox_vars):
                if var.get() == 1:
                    self.delays[i] = delay
            self.update_frame_list()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for delay.")

    def focus_delay_entry(self, event=None):
        """Set focus to the delay entry field and scroll to the current frame."""
        self.delay_entry.focus_set()
        self.focus_current_frame()
    
    def focus_current_frame(self):
        """Ensure the current frame is visible in the frame list."""
        if self.frame_list.winfo_children():
            frame_widgets = self.frame_list.winfo_children()
            current_frame_widget = frame_widgets[self.frame_index]
            self.canvas.yview_moveto(current_frame_widget.winfo_y() / self.canvas.bbox("all")[3])

    def show_about(self):
        """Display the About dialog."""
        messagebox.showinfo("About GIFCraft", "GIFCraft - GIF Editor\nVersion 1.0\n© 2024 by Seehrum")

    def setup_frame_list(self):
        """Set up the frame list with scrollbar."""
        self.frame_list_frame = Frame(self.master)
        self.frame_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = Scrollbar(self.frame_list_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = Canvas(self.frame_list_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)

        self.frame_list = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_list, anchor='nw')

        # Ensure the frame list is properly resized and configured to update the scrollbar
        self.frame_list.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.update_frame_list()

    def setup_control_frame(self):
        """Set up the control frame with image display."""
        self.control_frame_canvas = tk.Canvas(self.master)
        self.control_frame_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.control_frame_scrollbar = Scrollbar(self.control_frame_canvas, orient="vertical", command=self.control_frame_canvas.yview)
        self.control_frame_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.control_frame = tk.Frame(self.control_frame_canvas)
        self.control_frame_canvas.create_window((0, 0), window=self.control_frame, anchor='nw')

        self.control_frame_canvas.config(yscrollcommand=self.control_frame_scrollbar.set)
        self.control_frame.bind("<Configure>", lambda e: self.control_frame_canvas.config(scrollregion=self.control_frame_canvas.bbox("all")))

        # Frame for image display
        self.image_display_frame = tk.Frame(self.control_frame)
        self.image_display_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

        # Add a border to the image_label
        self.image_label = tk.Label(self.image_display_frame, bd=0, relief="flat")  # No border initially
        self.image_label.pack()

        self.dimension_label = tk.Label(self.image_display_frame, text="", font=("Arial", 8), fg="grey")
        self.dimension_label.pack(pady=5)

        self.total_duration_label = tk.Label(self.image_display_frame, text="", font=("Arial", 8), fg="grey")
        self.total_duration_label.pack(pady=5)

        # Frame for control inputs
        self.control_inputs_frame = tk.Frame(self.control_frame)
        self.control_inputs_frame.grid(row=1, column=0, padx=20, pady=10, sticky='n')

        self.delay_label = tk.Label(self.control_inputs_frame, text="Frame Delay (ms):")
        self.delay_label.grid(row=0, column=0, pady=5, sticky=tk.E)

        vcmd = (self.master.register(self.validate_delay), '%P')
        self.delay_entry = tk.Entry(self.control_inputs_frame, validate='key', validatecommand=vcmd)
        self.delay_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        self.delay_button = tk.Button(self.control_inputs_frame, text="Set Frame Delay", command=self.set_delay)
        self.delay_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.play_button = tk.Button(self.control_inputs_frame, text="Play", command=self.toggle_play_pause)
        self.play_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Make sure the window is scrolled to the correct size
        self.control_frame.update_idletasks()
        self.control_frame_canvas.config(scrollregion=self.control_frame.bbox("all"))

    def validate_delay(self, new_value):
        """Validate that the delay entry contains only digits."""
        if new_value.isdigit() or new_value == "":
            return True
        else:
            return False

    def bind_keyboard_events(self):
        """Bind keyboard events for navigating frames."""
        self.delay_entry.bind("<Return>", self.set_delay)
        self.master.bind("<Control-n>", self.new_file)
        self.master.bind("<Control-N>", self.new_file)
        self.master.bind("<Control-o>", self.load_file)
        self.master.bind("<Control-O>", self.load_file)
        self.master.bind("<Left>", self.previous_frame)
        self.master.bind("<Control-Left>", self.go_to_beginning)
        self.master.bind("<Right>", self.next_frame)
        self.master.bind("<Control-Right>", self.go_to_end)
        self.master.bind("<Up>", self.move_frame_up)
        self.master.bind("<Down>", self.move_frame_down)
        self.master.bind("<Delete>", self.delete_frames)
        self.master.bind("<Control-Delete>", self.delete_unchecked_frames)
        self.master.bind("<space>", self.toggle_play_pause)
        self.master.bind("<Control-c>", self.copy_frames)
        self.master.bind("<Control-C>", self.copy_frames)
        self.master.bind("<Control-v>", self.paste_frames)
        self.master.bind("<Control-V>", self.paste_frames)
        self.master.bind("<Control-z>", self.undo)
        self.master.bind("<Control-Z>", self.undo)
        self.master.bind("<Control-y>", self.redo)
        self.master.bind("<Control-Y>", self.redo)
        self.master.bind("<Control-s>", self.save)
        self.master.bind("<Control-S>", self.save_as)
        self.master.bind("x", self.toggle_checkbox)
        self.master.bind("X", self.toggle_checkbox)
        self.master.bind("w", self.toggle_draw_mode)
        self.master.bind("W", self.toggle_draw_mode)
        self.master.bind("a", self.toggle_check_all)
        self.master.bind("A", self.toggle_check_all)
        self.master.bind("t", self.toggle_transparent_frames_preview)
        self.master.bind("T", self.toggle_transparent_frames_preview)
        self.master.bind("f", self.focus_delay_entry)
        self.master.bind("F", self.focus_delay_entry)

    def toggle_checkbox(self, event=None):
        """Toggle the checkbox of the current frame."""
        if self.checkbox_vars:
            current_var = self.checkbox_vars[self.frame_index]
            current_var.set(0 if current_var.get() else 1)

    def next_frame(self, event=None):
        """Show the next frame without altering the scrollbar position."""
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 1
            self.show_frame()

    def go_to_end(self, event=None):
        """Move the cursor to the end of the frame list."""
        if self.frames:
            self.frame_index = len(self.frames) - 1
            self.show_frame()
            self.focus_current_frame()

    def previous_frame(self, event=None):
        """Show the previous frame without altering the scrollbar position."""
        if self.frame_index > 0:
            self.frame_index -= 1
            self.show_frame()

    def go_to_beginning(self, event=None):
        """Move the cursor to the beginning of the frame list."""
        if self.frames:
            self.frame_index = 0
            self.show_frame()
            self.focus_current_frame()

    def resize_to_base_size(self, image):
        """Resize the image to the base size of the first frame and center it."""
        if hasattr(self, 'base_size'):
            base_width, base_height = self.base_size
            new_image = Image.new("RGBA", self.base_size, (0, 0, 0, 0))
            image = image.resize(self.base_size, Image.Resampling.LANCZOS)
            new_image.paste(image, ((base_width - image.width) // 2, (base_height - image.height) // 2))
            return new_image
        return image

    def update_frame_list(self):
        """Update the frame list with the current frames and their delays."""
        # Clear existing widgets
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        # Display message if no frames are available
        if not self.frames:
            tk.Label(self.frame_list, text="No frames available").pack()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            return

        # Create and populate frame widgets
        for i, (frame, delay, var) in enumerate(zip(self.frames, self.delays, self.checkbox_vars)):
            frame_container = Frame(self.frame_list, bg='gray' if i == self.frame_index else self.frame_list.cget('bg'))
            frame_container.pack(fill=tk.X)

            checkbox = Checkbutton(frame_container, variable=var, bg=frame_container.cget('bg'))
            checkbox.pack(side=tk.LEFT)

            frame_label_text = f"Frame {i + 1}: {delay} ms"
            if i == self.frame_index:
                frame_label_text = f"→ {frame_label_text}"

            label = tk.Label(frame_container, text=frame_label_text, bg=frame_container.cget('bg'))
            label.pack(side=tk.LEFT, fill=tk.X)

        # Update the scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def set_current_frame(self, index):
        """Set the current frame to the one corresponding to the clicked checkbox."""
        self.frame_index = index
        self.show_frame()

    def show_frame(self):
        """Display the current frame."""
        if self.frames:
            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1  # Ensure the frame index is within bounds
            frame = self.frames[self.frame_index]
            preview = self.resize_image(frame, max_width=self.preview_width, max_height=self.preview_height)
            photo = ImageTk.PhotoImage(preview)
            self.image_label.config(image=photo, bd=2, relief="solid")  # Add border when frames are available
            self.image_label.image = photo
            self.image_label.config(text='')  # Remove text when showing image
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, str(self.delays[self.frame_index]))
            self.dimension_label.config(text=f"Size: {frame.width}x{frame.height}")  # Show frame dimensions
            total_duration = sum(self.delays)
            self.total_duration_label.config(text=f"Total Duration: {total_duration} ms")  # Show total duration
        else:
            self.image_label.config(image='', text="No frames to display", bd=0, relief="flat")  # Remove border when no frames
            self.image_label.image = None
            self.delay_entry.delete(0, tk.END)
            self.dimension_label.config(text="")  # Clear frame dimensions
            self.total_duration_label.config(text="")  # Clear total duration
        self.update_frame_list()  # Refresh the frame list to show the current frame indicator


    def save_state(self):
        """Save the current state for undo functionality."""
        self.history.append((self.frames.copy(), self.delays.copy(), [var.get() for var in self.checkbox_vars], self.frame_index, self.current_file))
        self.redo_stack.clear()  # Clear the redo stack on new action

    def resize_image(self, image, max_width, max_height):
        """Resize image while maintaining aspect ratio."""
        ratio = min(max_width / image.width, max_height / image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def main():
    """Main function to initialize the GIF editor."""
    root = tk.Tk()
    app = GIFEditor(master=root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted with Ctrl+C")
        root.destroy()


if __name__ == "__main__":
    main()
