import tkinter as tk

from easygui import *
# Tkinter Window
root_window = tk.Tk()

# Window Settings
root_window.title('Application Title')
root_window.geometry('300x100')
root_window.configure(background = '#353535')

# Text
tk.Label(root_window, text='Hello World', fg='White', bg='#353535').pack()

# Exit Button
tk.Button(root_window, text='Exit', width=10, command=root_window.destroy).pack()

# Main loop
root_window.mainloop()