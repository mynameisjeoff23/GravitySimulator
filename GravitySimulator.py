from tkinter import *


class Mass:
    def __init__(self):
        pass

class Simulator:
    def __init__(self) -> None:

        self.root = Tk()
        self.root.title("Gravity Simulator")
        self.root.state("zoomed")

        self.frame = Frame(self.root)
        self.frame.pack()

        self.canvas = Canvas(self.frame)
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=True)

        self.addMassButton = Button(self.canvas, text="+", command=self.addMass)
        self.addMassButton.pack()

        self.root.mainloop()
    
    def addMass(self) -> None:
        popup = Toplevel(self.canvas)
        popup.title("Select Mass Dimensions")
        popup.geometry("300x400")

        massText = Entry(popup)
        massText.pack()

        mass = massText.get()

        massText.bind("<")





if __name__ == "__main__": 
    sim = Simulator()