from tkinter import *
from time import time
from random import randint
import math
import ctypes

try: ctypes.windll.shcore.SetProcessDpiAwareness(1)

except: print("there was an exception trying to set dpi awareness")

G = 6.674215e-11
timeMultiplier = 1

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
        self.root.tk.call('tk', 'scaling', 1.0)  # Disable scaling
        self.root.state("zoomed")
        self.root.update_idletasks()
        
        self.frame = Frame(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.frame.pack(fill=BOTH, expand=True)

        self.canvas = Canvas(self.frame)
        self.canvas.pack(fill=BOTH, expand=True)

        self.masses = []
        self.massCount = 0

        #TODO: take buttons out of the canvas
        self.addMassButton = Button(self.canvas, text="+", command=self.addMass)
        self.addMassButton.pack()

        self.playButton = Button(self.canvas, text='  ▶ ', command=self.playHandler)
        self.playButton.pack()

        self.play = False

        self.root.mainloop()
    
    def addMass(self) -> None:
        self.popup = Toplevel(self.canvas)
        self.popup.title("Select Mass Dimensions")
        self.popup.geometry("200x100")
        # TODO: make pupup appear at the center 

        done = Button(self.popup, text="Done", command=self.closeAddMass)

        self.massText = Entry(self.popup)

        self.popup.bind("<Return>", self.closeAddMass)

        self.massText.pack() #TODO: change the packs into grids
        done.pack()
        self.popup.focus_force()
        self.massText.focus_set()

    def closeAddMass(self, canUsebutIDKWhatItDoes=None) -> None:# I don't know what the second argument does
                                                                # Other than prevent an exception
        if isfloat(x := self.massText.get()):
            self.mass = float(x)
            self.popup.destroy()
            self.masses.append(Mass(self))
            self.updateMassCount()
            self.mass = 0

    def updateMassCount(self) -> None:
        self.massCount = len(self.masses)

    def playHandler(self) -> None: 
        if self.play:
            self.play = False
            self.playButton.configure(text='  ▶ ')

        else:
            self.lastTime = time()
            self.play = True
            self.playButton.configure(text="  ▌▌")
            self.canvas.after(16, self.updateCallback)    
            self.canvas.after(16, self.updateVisuals)  

    def updateCallback(self) -> None: 
        if self.play:
            self.currentTime = time()
            self.deltaT = (self.currentTime - self.lastTime) * timeMultiplier
            for x in self.masses:
                x.updateAG()
            for x in self.masses:
                x.updatePos()
            self.lastTime = self.currentTime
            self.canvas.after(16, self.updateCallback)

    def updateVisuals(self) -> None:
        if self.play:
            for x in self.masses:
                self.canvas.coords(x.visualId, x.x - x.size, x.y - x.size, x.x + x.size, x.y + x.size)

        self.canvas.after(16, self.updateVisuals)
        #TODO: add another after(), fix after() call in updateCallBack()



class Mass:
    def __init__(self, main:Simulator, vi:list=[0.0, 0.0]) -> None:
        x = int(main.canvas.winfo_screenwidth()/2) #TODO: move this shit into the simulator
        y = int(main.canvas.winfo_screenheight()/2)
        self.main = main
        self.mass = main.mass
        self.size = 125 - 100/( 1 + 0.0001 * self.mass) # magic number
        self.x = x + randint(50 - x, x - 50) #temporaritly random
        self.y = y + randint(50 - y, y - 50)
        print(f"x: {self.x} y: {self.y}\nsize: {self.size}\n{x}x{y}")
        self.deltaV = [0.0, 0.0]
        self.vi = vi
        self.AG = [0.0, 0.0] # Acceleration due to gravity in (AGx, AGy) format

        # graphical stuff
        self.visualId = self.main.canvas.create_oval(self.x - self.size, self.y - self.size, \
                                                     self.x + self.size, self.y + self.size, \
                                                     fill="black", outline="black")
        print("should have posted a circle")

        
    def updateAG(self) -> None:
        notPast = True
        self.AG[0] = 0.0
        self.AG[1] = 0.0

        for x in self.main.masses:
            if notPast and self is x: #made confusing for short circuit
                notPast = False #skips calculating gravity when self is x
                continue # also skips checking if self is x if notPast == False
            else:   #calculate acceleration to another body
                deltaX = x.x - self.x
                deltaY = x.y - self.y
                theta = abs(math.atan(deltaY / deltaX))  # still dont know if this works but i guess we'll find out
                
                if deltaX < 0: xDir = -1
                elif deltaX > 0: xDir = 1
                else: xDir = 0

                if deltaY < 0: yDir = -1
                elif deltaY > 0: yDir = 1
                else: yDir = 0 

                r = math.sqrt(deltaX*deltaX + deltaY*deltaY)
                # (GMm/r^2) * 1/m, m being self.mass
                a = G * x.mass / (r*r)
                
                self.AG[0] += a * math.cos(theta) * xDir
                self.AG[1] += a * math.sin(theta) * yDir
        if not(int(time())%10):
            print(f"mass: {self.mass}\ta: {self.AG[0]:.8f}, {self.AG[1]:.8f}\tv: {self.vi[0]:.8f}, {self.vi[1]:.8f}\tpos: ({self.x:.8f}, {self.y:.8f})")
            print(f"deltaxy: ({deltaX:.8f}, {deltaY:.8f})\ttheta: {theta*180/math.pi:.8f}°\tr: {r}\tdir: ({xDir}, {yDir})")
    
    def updatePos(self):

        self.deltaV[0] = self.AG[0] * self.main.deltaT
        self.deltaV[1] = self.AG[1] * self.main.deltaT

        # xf = xi + vi + 1/2at^2
        # TODO: this might need to change to be reliant on vf = vi + at
        # I mean should produce same result, but at least test if v is the same
        self.x += self.vi[0] * self.main.deltaT + 0.5 * self.deltaV[0] * self.main.deltaT
        self.y += self.vi[1] * self.main.deltaT + 0.5 * self.deltaV[1] * self.main.deltaT

        # vf = vi + at
        self.vi[0] += self.deltaV[0]
        self.vi[1] += self.deltaV[1]

            


if __name__ == "__main__": 
    sim = Simulator()