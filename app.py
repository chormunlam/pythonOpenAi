import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()

window =tk.Tk()#make the window
window.title("chatGPT Language translation")
window.geometry("600x240")


# Get the screen width
screen_width = root.winfo_screenwidth()

# Set the minimum width
min_width = 500
root.minsize(width=min_width, height=200)

# Set the maximum width to the screen size
root.maxsize(width=screen_width, height=root.winfo_screenheight())




root.mainloop()
