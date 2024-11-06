from tkinter import *
from time import time
from random import randint
import math

G = 6.674215e-11

def isfloat(num) -> bool:
    try:
        float(num)
        return True
    except ValueError:
        return False
    


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

    def closeAddMass(self, canUsebutIDKWhatItDoes=None) -> None:# I don't know what the second argument does
                                                                # Other than prevent an exception
        if isfloat(x := self.massText.get()):
            self.mass = float(x)
            self.popup.destroy()
            self.masses.append(Mass(self.mass, self))
            self.mass = 0

            for i in self.masses:
                i.calculateAG()



class Mass:
    def __init__(self, mass:int, main:Simulator, size:int=50, vI:list=[0,0]) -> None:
        x = int(main.canvas.winfo_screenwidth()/2)
        y = int(main.canvas.winfo_screenheight()/2)
        self.main = main
        self.mass = mass
        self.size = size
        print(f"x: {x} y: {y}")
        self.x = x + randint(50 - x, x - 50)
        self.y = y + randint(50 - y, y - 50)
        self.lastTime = time()
        self.vI = vI
        self.AG = [0.0, 0.0]    # Acceleration due to gravity in (AGx, AGy) format

    def updateAG(self) -> None:
        notPast = True
        for x in self.main.masses:
            print(f"self is x: {self is x}")
            if notPast and self is x: #made confusing for short circuit
                notPast = False
                continue
            else:   #calculate acceleration to another body
                deltaX = x.x - self.x
                deltaY = x.y - self.y
                theta = math.atan2(deltaY, deltaX) # still dont know if this works but i guess well find out
                r = math.sqrt(deltaX*deltaX + deltaY*deltaY)
                A = G * self.mass * x.mass / (r*r)
                self.AG[0] += A * math.cos(theta)
                self.AG[1] += A * math.sin(theta)

    def updateV(self):
        currentTime = time()
        deltaT = currentTime - self.lastTime
        # vf = vi + at

        pass
            


if __name__ == "__main__": 
    sim = Simulator()