import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk, Button, Label
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from docx import Document

def load_mask_image():
    global mask_image_path
    mask_image_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if mask_image_path:
        label.config(text="Mask image loaded successfully.")
    else:
        label.config(text="Failed to load mask image. Please try again.")

def load_text_file():
    global text_file_path
    text_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Word documents", "*.docx")])
    if text_file_path:
        label.config(text="Text file loaded successfully.")
    else:
        label.config(text="Failed to load text file. Please try again.")

def read_text_from_file(path):
    if path.endswith('.docx'):
        document = Document(path)
        return "\n".join([paragraph.text for paragraph in document.paragraphs])
    else:  # Assuming the file is a .txt file
        with open(path, 'r') as file:
            return file.read()

def generate_word_cloud():
    if not mask_image_path or not text_file_path:
        label.config(text="Please load both files before generating the word cloud.")
        return
    
    # Load the image used as a mask/color template
    mask_image = np.array(Image.open(mask_image_path))
    
    # Load text from the file
    text = read_text_from_file(text_file_path)
    
    # Generate a word cloud image
    wordcloud = WordCloud(background_color='white', mode="RGBA", max_words=1000, mask=mask_image).generate(text)
    
    # Create coloring from image
    image_colors = ImageColorGenerator(mask_image)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=120)
    ax.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
    ax.axis("off")
    
    # Embedding the matplotlib plot in tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=3, column=0, columnspan=3)
    canvas.draw()

# Setup the tkinter GUI
root = Tk()
root.title("Word Cloud Generator")

label = Label(root, text="Please load a mask image and a text file.")
label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

button_load_mask = Button(root, text="Load Mask Image", command=load_mask_image)
button_load_mask.grid(row=1, column=0, padx=10, pady=10)

button_load_text = Button(root, text="Load Text File", command=load_text_file)
button_load_text.grid(row=1, column=1, padx=10, pady=10)

button_generate = Button(root, text="Generate Word Cloud", command=generate_word_cloud)
button_generate.grid(row=1, column=2, padx=10, pady=10)

root.mainloop()
