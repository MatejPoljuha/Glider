import tkinter as tk
from tkinter import ttk
from tkinter import * 

# this is the function called when the button is clicked
def ModeOne():
    print('clicked ONE')


# this is the function called when the button is clicked
def ModeTwo():
    print('clicked Two')


# this is a function to get the user input from the text input box
def getInputBoxValue():
    userInput = tInput.get()
    return userInput



root = Tk()

# This is the section of code which creates the main window
root.geometry('1000x600')
root.configure(background='#F0F8FF')
root.title('Glider Navigation System')
root.resizable(width=False, height=False)

# First, we create a canvas to put the picture on
MapCanvas= Canvas(root, height=500, width=500)
# Then, we actually create the image file to use (it has to be a *.gif)
picture_file = PhotoImage(file = 'lena.png')  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
# Finally, we create the image on the canvas and then place it onto the main window
MapCanvas.create_image(500, 0, anchor=NE, image=picture_file)
MapCanvas.place(x=10, y=10)


# This is the section of code which creates a button
Button(root, text='Longest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeOne).place(x=850, y=100)


# This is the section of code which creates a button
Button(root, text='Fastest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeTwo).place(x=850, y=150)


# This is the section of code which creates the a label
Label(root, text='Status', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=850, y=200)


# This is the section of code which creates a text input box
tInput=Entry(root)
tInput.place(x=850, y=250)


root.mainloop()
