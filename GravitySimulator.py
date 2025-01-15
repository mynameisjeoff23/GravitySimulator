from tkinter import *
from time import time
from random import randint
import math
import ctypes

try: ctypes.windll.shcore.SetProcessDpiAwareness(1)

except: print("there was an exception trying to set dpi awareness")

G_CONST = 6.674215e-11
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

        self.scale = 1.0
        self.masses = []
        self.massCount = 0
        self.dxy = [0.0, 0.0]

        #TODO: take buttons out of the canvas and put in frame
        self.addMassButton = Button(self.canvas, text="+", command=self.addMass)
        self.addMassButton.pack()

        self.playButton = Button(self.canvas, text='  ▶ ', command=self.playHandler)
        self.playButton.pack()

        self.play = False
        self.followMouse = False
        self.adding = False
        self.updateArrow = False

        self.root.mainloop()
    
    def askMass(self) -> None:
        self.popup = Toplevel(self.canvas)
        self.popup.title("Select Mass Dimensions")
        self.popup.geometry(f"200x100+{self.canvas.winfo_pointerx()}+{self.canvas.winfo_pointery()}")
        self.popup.protocol("WM_DELETE_WINDOW", self.cancelAdding)
        # TODO: make pupup appear at the center 

        done = Button(self.popup, text="Done", command=self.closeAskMass)

        self.massText = Entry(self.popup)

        self.popup.bind("<Return>", self.closeAskMass)

        self.massText.pack() #TODO: change the packs into grids
        done.pack()
        self.popup.focus_force() # set as focus window
        self.massText.focus_set() # make textbox ready for typing

    def addMass(self) -> None:
        if not(self.adding):
            self.adding = True
            self.followMouse = True
            self.canvas.bind("<Button-1>", self.mousePressed)
            self.canvas.bind("<ButtonRelease-1>", self.mouseReleased)
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.tempCircle = self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill = "black")
            self.canvas.after(15, self.updateTempCircle)

    def closeAskMass(self, event:Event=None) -> None:
        if isfloat(x := self.massText.get()) and (float(x) > 0): 
            self.mass = float(x)
            r = math.sqrt(self.dxy[0]**2 + self.dxy[1]**2)

            if r >= 3:
                vi = [self.dxy[0] / -5, self.dxy[1] / -5]
            else:
                vi = [0.0, 0.0]

            print(vi)

            self.popup.destroy()

            self.masses.append(Mass(self, vi.copy()))
            self.updateMassCount()
            self.canvas.delete(self.tempCircle)
            self.tempCircle = None
            self.mass = 0
            self.adding = False
            self.initial = (float(), float())
            self.dxy = [float(), float()]
            
    def updateMassCount(self) -> None:
        self.massCount = len(self.masses)

    def mousePressed(self, event:Event) -> None:
        if self.followMouse:
            self.followMouse = False
            self.updateArrow = True
            self.initial = (event.x, event.y)
            self.arrow = self.canvas.create_line(event.x, event.y, event.x, event.y, arrow=LAST)
            self.canvas.after(15, self.updateViPreview)

    def mouseReleased(self, event:Event) -> None:
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.delete(self.arrow)
        self.updateArrow = False
        
        self.askMass()

    def cancelAdding(self):
        self.popup.destroy()
        self.canvas.delete(self.tempCircle)
        self.followMouse = False
        self.adding = False
        self.updateArrow = False

    def playHandler(self) -> None: 
        if self.play:
            self.play = False
            self.playButton.configure(text='  ▶ ')

        else:
            self.lastTime = time()
            self.play = True
            self.playButton.configure(text="  ▌▌")
            self.canvas.after(15, self.updateCallback)    

    def updateTempCircle(self) -> None:
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        self.canvas.coords(self.tempCircle, x - 25, y - 25, x + 25, y + 25)
        if self.followMouse:
            self.canvas.after(15, self.updateTempCircle)

    def updateCallback(self) -> None: 
        if self.play:
            self.currentTime = time()
            self.deltaT = (self.currentTime - self.lastTime) * timeMultiplier
            #self.deltaT = 0.01694915254237288 * timeMultiplier
            for x in self.masses:
                if x.updateAG():
                    self.canvas.after(15, self.updateCallback)
                    return
            for x in self.masses:
                x.updatePos()
            self.lastTime = self.currentTime
            self.canvas.after(15, self.updateCallback)

            for x in self.masses:
                self.canvas.coords(x.visualId, x.x - x.size, x.y - x.size, x.x + x.size, x.y + x.size)

    def updateViPreview(self):
        if self.adding and not(self.followMouse) and self.updateArrow:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.dxy[0] = x - self.initial[0]
            self.dxy[1] = y - self.initial[1]
            r = math.sqrt(self.dxy[0]**2 + self.dxy[1]**2)
            if r >= 3:
                self.canvas.coords(self.arrow, self.initial[0], self.initial[1],\
                                    self.initial[0] + (self.dxy[0] / -2), \
                                    self.initial[1] + (self.dxy[1] / -2))
            else: 
                self.canvas.coords(self.arrow, self.initial[0], self.initial[1], self.initial[0], self.initial[1])
            
            self.canvas.after(15, self.updateViPreview)



    def collide(self, obj1, obj2):
        cm = [0.0, 0.0]
        #cm = (m1x1 + m2x2)/(m1 + m2)
        mTot = obj1.mass + obj2.mass
        cm[0] = (obj1.mass * obj1.x + obj2.mass * obj2.x)/(mTot)
        cm[1] = (obj1.mass * obj1.y + obj2.mass * obj2.y)/(mTot)
        # m1v1 + m2v2 = mfvf
        pSys = [(obj1.P[0] + obj2.P[0]), (obj1.P[1] + obj2.P[1])]
        # vf = (m1v1 + m2v2)/mf
        vf = [(pSys[0]/(mTot)), (pSys[1]/(mTot))]

        if obj1.mass < obj2.mass:
            obj2.afterCollision(mTot, vf, cm)
            self.canvas.delete(obj1.visualId)
            self.masses.pop(self.masses.index(obj1))
        else: 
            obj1.afterCollision(mTot, vf, cm)
            self.canvas.delete(obj2.visualId)
            self.masses.pop(self.masses.index(obj2))
            


class Mass:
    def __init__(self, main:Simulator, vi:list=None) -> None:
        self.main = main
        self.mass = main.mass 
        #self.size = 125 - 100/( 1 + 0.0001 * self.mass) # magic number TODO: change when adding zooming to be logarithmic
        self.size = 10 * math.log(self.mass + 250) - 30.21461
        self.x = self.main.initial[0]
        self.y = self.main.initial[1]

        print(f"x: {self.x} y: {self.y}\nsize: {self.size}")
        self.deltaV = [0.0, 0.0]
        if vi == None:
            self.vi = [0.0, 0.0]
        else: 
            self.vi = vi
        self.P = [(self.vi[0] * self.mass), (self.vi[1] * self.mass)] # momentum as (Px, Py)
        self.AG = [0.0, 0.0] # Acceleration due to gravity in (AGx, AGy) format

        # graphical stuff
        self.visualId = self.main.canvas.create_oval(self.x - self.size, self.y - self.size, \
                                                     self.x + self.size, self.y + self.size, \
                                                     fill="black", outline="black")
        print("should have posted a circle")

        
    def updateAG(self) -> int:
        notPast = True
        self.AG[0] = 0.0
        self.AG[1] = 0.0

        for i in self.main.masses:
            if notPast and self is i: #made confusing for short circuit
                notPast = False #skips calculating gravity when self is x
                continue # also skips checking if self is x if notPast == False
            else:   #calculate acceleration to another body
                deltaX = i.x - self.x + 1e-15
                deltaY = i.y - self.y + 1e-15

                #TODO:handle deltas of 0
                if not deltaX:
                    print("This shouldn't be possible, deltaX = 0") # actually it is, just improbable
                    print(id(self))
                    print(id(i))
                    exit()

                r = math.sqrt(deltaX*deltaX + deltaY*deltaY)

                if r < max(self.size, i.size):
                    self.main.collide(self, i)
                    return 1              

                theta = abs(math.atan(deltaY / deltaX))
                
                if deltaX < 0: xDir = -1
                elif deltaX > 0: xDir = 1
                else: xDir = 0

                if deltaY < 0: yDir = -1
                elif deltaY > 0: yDir = 1
                else: yDir = 0 

                # (GMm/r^2) * 1/m, m being self.mass
                a = G_CONST * i.mass / (r*r)
                
                self.AG[0] += a * math.cos(theta) * xDir
                self.AG[1] += a * math.sin(theta) * yDir
        
        return 0
    
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

        self.P[0] = (self.vi[0] * self.mass)
        self.P[1] = (self.vi[1] * self.mass)
    
    def afterCollision(self, new:float, vf:list, cm:list) -> None:

        self.mass = new
        self.size = 10 * math.log(self.mass + 250) - 30.21461
        self.main.canvas.coords(self.visualId, self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size)

        self.x = cm[0]
        self.y = cm[1]

        self.vi = vf
        


if __name__ == "__main__": 
    sim = Simulator()