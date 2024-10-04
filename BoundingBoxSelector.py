#finally works the capture screenshot took so much work
#remember to set adc credentials  by set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Seaking!!!\Downloads\mtl-service-account-keys(1).json


import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk,ImageDraw,ImageFont
import pyautogui
import datetime
import json
import tkinter.simpledialog as simpledialog
starting_pos = 0
ending_pos = 0
class BoundingBoxSelector:
    def __init__(self, master):
        self.master = master
        self.master.title("Bounding Box Selector")

        self.canvas = tk.Canvas(master, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.images = []
        self.image_paths = []
        self.current_image_index = None
        self.resized_image = None
        self.photo = None
        self.bbox = None
        self.rect = None
        self.locked = False

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.master.bind("<KeyPress-l>", self.toggle_lock_bbox)

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_images)
        file_menu.add_command(label="Exit", command=master.quit)
        file_menu.add_command(label="Open Folder", command=self.open_folder)

        self.start_x = None
        self.start_y = None

        # Navigation buttons
        self.prev_button = tk.Button(master, text="Previous", command=self.show_previous_image)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(master, text="Next", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT)

        # Save and Load buttons
        self.save_button = tk.Button(master, text="Save", command=self.save_bbox)
        self.save_button.pack(side=tk.LEFT)

        self.load_button = tk.Button(master, text="Load", command=self.load_bbox)
        self.load_button.pack(side=tk.LEFT)

        # Screenshot button
        self.screenshot_button = tk.Button(master, text="Screenshot", command=self.capture_content)
        self.screenshot_button.pack(side=tk.LEFT)

        # Fill button
        self.screenshot_button = tk.Button(master, text="Fill", command=self.fill_bg_white)
        self.screenshot_button.pack(side=tk.LEFT)
        
        # Button to fill bounding box with text
        self.fill_text_button = tk.Button(master, text="Fill Text", command=self.fill_bg_with_text_prompt)
        self.fill_text_button.pack(side=tk.LEFT)

        self.fill_text_button = tk.Button(master, text="Translate", command=self.translate)
        self.fill_text_button.pack(side=tk.LEFT)

        self.fill_text_button = tk.Button(master, text="Save Image", command=self.save_current_image)
        self.fill_text_button.pack(side=tk.LEFT)

        self.open_folder_button = tk.Button(master, text="Open Folder", command=self.open_folder)
        self.open_folder_button.pack(side=tk.LEFT)

    def open_images(self):
        file_paths = filedialog.askopenfilenames()
        if not file_paths:
            return
        for file_path in file_paths:
            try:
                image = Image.open(file_path)
                self.images.append(image)
                self.image_paths.append(file_path)
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
        if self.images:
            self.current_image_index = 0
            self.display_image()

    def display_image(self):
        if self.current_image_index is not None and self.current_image_index < len(self.images):
            image = self.images[self.current_image_index]
            print(f"Displaying image: {self.image_paths[self.current_image_index]}")
            print(f"Image dimensions: {image.width} x {image.height}")
            self.resize_image_to_canvas(image)
            if self.resized_image:
                self.photo = ImageTk.PhotoImage(self.resized_image)
                self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
            self.bbox = None
            self.locked = False
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = None

    def resize_image_to_canvas(self, image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = image.size

        if canvas_width >= image_width and canvas_height >= image_height:
            self.resized_image = image
            return

        if canvas_width < image_width and canvas_height < image_height:
            scale = min(canvas_width / image_width, canvas_height / image_height)
            new_width = int(image_width * scale)
            new_height = int(image_height * scale)
        elif canvas_width < image_width:
            scale = canvas_width / image_width
            new_width = canvas_width
            new_height = int(image_height * scale)
        else:  # canvas_height < image_height
            scale = canvas_height / image_height
            new_width = int(image_width * scale)
            new_height = canvas_height

        self.resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def show_previous_image(self):
        if self.current_image_index is not None and self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image()

    def show_next_image(self):
        if self.current_image_index is not None and self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.display_image()

    def on_button_press(self, event):
        if self.locked:
            return
        self.start_x = event.x
        self.start_y = event.y
        global starting_pos
        starting_pos = pyautogui.position()
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        if self.locked:
            return
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        global ending_pos
        ending_pos = pyautogui.position()
        

    def on_button_release(self, event):
        if self.locked:
            return
        end_x, end_y = (event.x, event.y)
        self.bbox = (self.start_x, self.start_y, end_x, end_y)
        print(f"Bounding Box Coordinates: {self.bbox}")
        print(f"pyautogui pos{starting_pos,ending_pos}")

    def toggle_lock_bbox(self, event):
        self.locked = not self.locked
        state = "Locked" if self.locked else "Unlocked"
        print(f"Bounding Box {state}: {self.bbox}")

    def save_bbox(self):
        if self.bbox is None:
            print("No bounding box to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        data = {
            "image_path": self.image_paths[self.current_image_index],
            "bounding_box": self.bbox
        }
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f)
            print(f"Bounding box saved to {file_path}")
        except Exception as e:
            print(f"Error saving bounding box: {e}")

    def load_bbox(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            image_path = data.get("image_path")
            bbox = data.get("bounding_box")
            if image_path in self.image_paths:
                self.current_image_index = self.image_paths.index(image_path)
                self.display_image()
                self.bbox = bbox
                self.start_x, self.start_y, end_x, end_y = bbox
                if self.rect:
                    self.canvas.delete(self.rect)
                self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red")
                self.locked = True
                print(f"Loaded bounding box from {file_path}")
            else:
                print(f"Image path {image_path} not found in loaded images.")
        except Exception as e:
            print(f"Error loading bounding box: {e}")


    def capture_content(self):
        bbox = self.get_locked_bbox_coordinates()
        if bbox is None:
            return

        x1, y1, x2, y2 = bbox
        width, height = x2 - x1, y2 - y1
        all_pos = list(starting_pos)
        all_pos.append(width)
        all_pos.append(height)
        all_pos_final = tuple(all_pos)

        print(f"Capturing content with coordinates: {all_pos_final}")
        
        screenshot = pyautogui.screenshot(region = (all_pos_final))
        screenshot.save("input.png")
        print("Content within locked bounding box captured and saved as 'input.png'")

    def get_locked_bbox_coordinates(self):
        if not self.locked or not self.bbox:
            print("No bounding box to capture or bounding box not locked.")
            return None
        # Adjust the coordinates based on the scaling factor
        x1, y1, x2, y2 = self.bbox
        if self.resized_image:
            scale_x = self.images[self.current_image_index].width / self.resized_image.width
            scale_y = self.images[self.current_image_index].height / self.resized_image.height
            x1, y1, x2, y2 = [int(coord * scale) for coord, scale in zip(self.bbox, [scale_x, scale_y, scale_x, scale_y])]
            print(f"Bounding box coordinates (original): ({x1}, {y1}, {x2}, {y2})")
        return x1, y1, x2, y2

    def fill_bg_white(self):
        bbox = self.get_locked_bbox_coordinates()
        if bbox is None:
            print("Fill unsuccessful, no box detected")
            return

        x1, y1, x2, y2 = bbox
        image = self.images[self.current_image_index].copy().convert("RGBA")
        draw = ImageDraw.Draw(image, "RGBA")
        
        # Fill the bounding box with white
        draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, 255))
        
        # Update the image in the list and redisplay it
        self.images[self.current_image_index] = image
        self.display_image()

        print("Bounding box filled with white")

    def fill_bg_with_text(self, text):
        image = self.images[self.current_image_index].copy()
        draw = ImageDraw.Draw(image)

        if self.bbox:
            x1, y1, x2, y2 = self.get_locked_bbox_coordinates()
            bbox_width = x2 - x1
            bbox_height = y2 - y1

            # Calculate font size based on the bounding box dimensions
            font_size = min(bbox_width, bbox_height) // 10
            if font_size < 30:
                font_size = 30

            font = ImageFont.truetype("arial.ttf", font_size)
            
            # Split text into multiple lines if necessary
            lines = [text]
            if font_size == 20:
                max_width = bbox_width - 10
                avg_char_width = font.getbbox("A")[2] - font.getbbox("A")[0]
                max_chars_per_line = max_width // avg_char_width
                words = text.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    if sum([font.getbbox(w)[2] - font.getbbox(w)[0] for w in current_line]) > max_width:
                        lines.append(" ".join(current_line[:-1]))
                        current_line = [word]
                lines.append(" ".join(current_line))

            # Adjust position to center the text within the bounding box
            total_text_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines])
            start_y = y1 + (bbox_height - total_text_height) // 2

            draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, 255))
            
            current_y = start_y
            for line in lines:
                text_bbox = font.getbbox(line)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (bbox_width - text_width) // 2
                draw.text((text_x, current_y), line, fill=(0, 0, 0, 255), font=font)
                current_y += text_bbox[3] - text_bbox[1]

        self.images[self.current_image_index] = image
        self.display_image()
        print(f"Bounding box filled with text: {text}")

    def save_current_image(self):
        if self.current_image_index is not None and self.current_image_index < len(self.images):
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if not file_path:
                return
            try:
                self.images[self.current_image_index].save(file_path)
                print(f"Image saved to {file_path}")
            except Exception as e:
                print(f"Error saving image: {e}")

    

    def fill_bg_with_text_prompt(self):
        text = simpledialog.askstring("Input", "Enter text to fill:")
        if text:
            self.fill_bg_with_text(text)


    def google_ocr(self,path):
        """Detects text in the file."""
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()

        with open(path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        print("Texts:")
        No_of_text = 0
        for text in texts:
            print(f'\n"{text.description}"')
            if No_of_text == 0 :
                return text.description

        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )
    def deepl_translate(self,input_text):
        import deepl

        auth_key = ""  # Replace with your key

        translator = deepl.Translator(auth_key)
        
        result = translator.translate_text(input_text, target_lang="EN-US")
        print(result)
        print(result.text)  

        return result.text

    
    def translate(self):
        path = "input.png" # for now not to overcomplicate.Change if it causes issues
        #First get the screenshot and it's path to send to the google's cloud vision api
        #Second get the ocr text
        #Third translate the ocr text
        #Fourth paste the translated text
        if self.locked :
            self.capture_content()
            ocr_text = self.google_ocr(path)
            translated_text = self.deepl_translate(ocr_text)
            self.fill_bg_with_text(translated_text)
    
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        self.open_images_from_folder(folder_path)
    
    def carry_over_images(self,carry_over_image_path): # To carryover images that display error in the comic.py program
        self.image_paths = carry_over_image_path
        if self.image_paths is None:
            root = tk.Tk()
            app = BoundingBoxSelector(root)
            root.mainloop()
        else :
            self.display_image()

    def open_images_from_folder(self, folder_path):
            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
            file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            
            if not file_paths:
                print(f"No images found in folder: {folder_path}")
                return
            
            for file_path in file_paths:
                try:
                    image = Image.open(file_path)
                    self.images.append(image)
                    self.image_paths.append(file_path)
                except Exception as e:
                    print(f"Error loading image {file_path}: {e}")
            
            if self.images:
                self.current_image_index = 0
                self.display_image()


#if __name__ == "__main__":
root = tk.Tk()
app = BoundingBoxSelector(root)
root.mainloop()
