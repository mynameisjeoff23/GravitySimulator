from tkinter import *


def isfloat(num) -> bool:
    try:
        float(num)
        return True
    except ValueError:
        return False

class Mass:
    def __init__(self, mass:int) -> None:
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

        self.masses = []

        self.addMassButton = Button(self.canvas, text="+", command=self.addMass)
        self.addMassButton.pack()

        self.root.mainloop()
    
    def addMass(self) -> None:
        self.popup = Toplevel(self.canvas)
        self.popup.title("Select Mass Dimensions")
        self.popup.geometry("200x100")

        done = Button(self.popup, text="Done", command=self.closeAddMass)

        self.massText = Entry(self.popup)
        self.massText.bind("<Enter>", self.closeAddMass)

        self.massText.pack() #TODO: change the packs into grids
        done.pack()

    def closeAddMass(self, optionalVariableWhichForSomeReasonIDKIsPassed=None) -> None: # I don't know what the second positional argument does
                                                                                        # Other than calm down exception warnings
        if isfloat(x := self.massText.get()):
            self.mass = float(x)
            self.popup.destroy()
            self.masses.append(Mass(self.mass))



if __name__ == "__main__": 
    sim = Simulator()