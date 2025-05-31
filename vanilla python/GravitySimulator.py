from tkinter import *
from time import time
import math
import ctypes

try: ctypes.windll.shcore.SetProcessDpiAwareness(1)

except: print("there was an exception trying to set dpi awareness")

G_CONST = 6.674215e-11

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
        
        self.frame = Frame(self.root, height=50, bg="light grey")
        self.frame.pack(side=TOP, fill="x")

        self.canvas = Canvas(self.root)
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.mousePressed)
        self.canvas.bind("<ButtonRelease-1>", self.mouseReleased)
        self.root.bind("<Escape>", self.rootEscapeHandler)
        self.canvas.bind("<MouseWheel>", self.mouseWheelHandler)

        self.scale = 1.0
        self.timeScale = 1.0
        self.masses = []
        self.massCount = 0
        self.dxy = [0.0, 0.0]
        self.xOffset = 0.0
        self.yOffset = 0.0
        self.vi = [0.0, 0.0]
        self.iterations = range(1)
        self.deltaT = 0.0
        self.screenToWorldX = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        self.screenToWorldY = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()

        self.addMassButton = Button(self.frame, text="+", command=self.addMass, width=10, font=("Arial", 20))
        self.addMassButton.pack(side=LEFT, padx = 5, pady=5)

        self.playButton = Button(self.frame, text='  ▶ ', command=self.playHandler, width=10, font=("Arial", 20))
        self.playButton.pack(side=LEFT, padx=5, pady=5)

        self.clearButton = Button(self.frame, text='    🗑️', command=self.clearHandler, width=10, font=("Arial", 20))
        self.clearButton.pack(side=LEFT, padx=5, pady=5)

        self.timeSlider = Scale(self.frame, from_=1, to=47, showvalue=0, width=25, length=200, orient=HORIZONTAL, command=self.timeHandler, resolution=1)
        self.timeSlider.set(10)
        self.timeSlider.pack(side=LEFT, padx=5, pady=5)
        self.timeStr = StringVar()
        self.timeStr.set("Time: 1.0x")
        self.timeLbl = Label(self.frame, textvariable=self.timeStr, font=("Arial", 20))
        self.timeLbl.pack(side=LEFT, pady=5)

        self.mouseCoordStr = StringVar()
        self.mouseCoordStr.set(f"({self.screenToWorldX}, {self.screenToWorldY})")
        self.mouseCoordLbl = Label(self.canvas, textvariable=self.mouseCoordStr, anchor=W)
        self.canvas.create_window(0, 0, anchor=NW, window=self.mouseCoordLbl)

        self.framesTime = time()
        self.frames = 0
        self.framesStr = StringVar()
        self.framesStr.set("FPS: 0")
        self.framesLbl = Label(self.canvas, textvariable=self.framesStr, anchor=W)
        self.canvas.create_window(100, 0, anchor=NW, window=self.framesLbl)

        self.play = False
        self.followMouse = False
        self.adding = False
        self.updateArrow = False
        self.panning = False
        

        self.lastTime = time()
        self.canvas.after(15, self.updateCallback)
        self.canvas.after(1000, self.framesCallback)
        self.root.mainloop()
    
    def askMass(self, mouseX, mouseY) -> None:

        # Get the root window's position and dimensions
        rootX = self.canvas.winfo_x()
        rootY = self.canvas.winfo_y()
        rootWidth = self.canvas.winfo_width()
        rootHeight = self.canvas.winfo_height()

        cursorX = mouseX
        cursorY = mouseY

        toplevelWidth = 200
        toplevelHeight = 100

        # Calculate default Toplevel position
        newX = cursorX
        newY = cursorY

        # Adjust if the Toplevel window would go outside the root boundaries
        if cursorX + toplevelWidth > rootX + rootWidth:
            newX = rootX + rootWidth - toplevelWidth
        if cursorY + toplevelHeight > rootY + rootHeight:
            newY = rootY + rootHeight - toplevelHeight

        # Ensure Toplevel doesn't go above or to the left of the root window
        if newX < rootX:
            newX = rootX
        if newY < rootY:
            newY = rootY

        self.popup = Toplevel(self.canvas)
        self.popup.title("Select Mass Dimensions")
        self.popup.geometry(f"{toplevelWidth}x{toplevelHeight}+{newX}+{newY}")
        self.popup.protocol("WM_DELETE_WINDOW", self.cancelAdding)

        done = Button(self.popup, text="Done", command=self.closeAskMass)

        self.massText = Entry(self.popup)

        self.popup.bind("<Return>", self.closeAskMass)
        self.popup.bind("<Escape>", self.popupEscapeHandler)

        self.massText.pack()
        done.pack()
        self.popup.focus_force() # set as focus window
        self.massText.focus_set() # make textbox ready for typing

    def addMass(self) -> None:
        if not(self.adding):
            self.adding = True
            self.followMouse = True
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.tempCircle = self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill = "black")
            self.canvas.after(15, self.updateTempCircle)

    def closeAskMass(self, event:Event=None) -> None:
        if isfloat(x := self.massText.get()) and (float(x) > 0): 
            self.mass = float(x)

            self.popup.destroy()

            self.masses.append(Mass(self, self.vi.copy()))
            self.updateMassCount()
            self.canvas.delete(self.tempCircle)
            self.tempCircle = None
            self.mass = 0.0
            self.adding = False
            self.initial = (float(), float())
            self.dxy = [float(), float()]
            
    def updateMassCount(self) -> None:
        self.massCount = len(self.masses)

    def mousePressed(self, event:Event) -> None:
        if self.followMouse:
            self.followMouse = False
            self.updateArrow = True
            self.initial = (float(event.x), float(event.y))
            self.arrow = self.canvas.create_line(event.x, event.y, event.x, event.y, arrow=LAST)
            self.canvas.after(15, self.updateViPreview)

        if (not self.adding) and (not self.panning):
            self.panning = True
            self.lastX = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            self.lastY = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.canvas.after(15, self.updateOffset)
            

    def mouseReleased(self, event:Event) -> None:
        if self.updateArrow:
            self.canvas.delete(self.arrow)
            self.updateArrow = False
            self.askMass(event.x, event.y)

        if self.panning:
            self.panning = False


    def rootEscapeHandler(self, event:Event) -> None:
        if self.adding:
            self.canvas.delete(self.tempCircle)
            self.canvas.delete(self.arrow)
            self.adding = False
            self.followMouse = False
            self.updateArrow = False

    def popupEscapeHandler(self, event:Event) -> None:
        if self.adding:
            self.cancelAdding()

    def mouseWheelHandler(self, event:Event) -> None:
        # screen to world before
        x0 = event.x / self.scale - self.xOffset
        y0 = event.y / self.scale - self.yOffset

        magnitude = abs(event.delta)//120

        if event.delta < 0:
            for x in range(magnitude):
                self.scale *= .95

        elif event.delta > 0:
            for x in range(magnitude):
                self.scale *= 1.05
                
        x1 = event.x / self.scale - self.xOffset
        y1 = event.y / self.scale - self.yOffset

        self.xOffset += x1 - x0
        self.yOffset += y1 - y0

    def timeHandler(self, timeScale):
        x = int(timeScale)

        # scaleTotal = timeScale * iterations 
        if x < 11:
            self.iterations = range(1)
            self.timeScale = x * .1
        elif x < 21:
            self.iterations = range(2)
            self.timeScale = x * .05
        elif x < 30:
            self.iterations = range(x - 18)
            self.timeScale = 1.0
        else:
            self.iterations = range(5 * x - 135)
            self.timeScale = 1.0

        self.timeStr.set(f"Time: {self.timeScale * (self.iterations[-1] + 1):.1f}x")
    

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

    def updateTempCircle(self) -> None:
        if self.followMouse:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.canvas.coords(self.tempCircle, x - 25, y - 25, x + 25, y + 25)
            self.canvas.after(15, self.updateTempCircle)

    def updateCallback(self) -> None: 

        for x in self.masses:
            # world to screen coordinates
            self.canvas.coords(x.visualId, (x.x - x.size + self.xOffset) * self.scale, (x.y - x.size + self.yOffset) * self.scale,\
                              (x.x + x.size + self.xOffset) * self.scale, (x.y + x.size + self.yOffset) * self.scale)

        self.screenToWorldX = (self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()) / self.scale - self.xOffset 
        self.screenToWorldY = (self.canvas.winfo_pointery() - self.canvas.winfo_rooty()) / self.scale - self.yOffset 

        if self.adding:       
            r = math.sqrt(self.dxy[0]**2 + self.dxy[1]**2)

            if r >= 3:
                self.vi[0] = self.dxy[0] / -5 / self.scale
                self.vi[1] = self.dxy[1] / -5 / self.scale
            else:
                self.vi = [0.0, 0.0]

            self.mouseCoordStr.set(f"({self.screenToWorldX:.0f}, {self.screenToWorldY:.0f})\nv: {math.sqrt(self.vi[0]**2 + self.vi[1]**2):.2f}")
            
        else:
            self.mouseCoordStr.set(f"({self.screenToWorldX:.0f}, {self.screenToWorldY:.0f})")


        if self.play:
            self.currentTime = time()
            self.deltaT = (self.currentTime - self.lastTime) * self.timeScale
            #self.deltaT = 0.01694915254237288 * self.timeScale
            for x in self.iterations:
                for x in self.masses:
                    if x.updateAG():
                        self.canvas.after(15, self.updateCallback)
                        return
                for x in self.masses:
                    x.updatePos()
                self.lastTime = self.currentTime
            
        self.frames += 1
        self.canvas.after(15, self.updateCallback)    


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

    def updateOffset(self):
        if self.panning:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.xOffset += (x - self.lastX) / self.scale
            self.yOffset += (y - self.lastY) / self.scale
            self.lastX = x  
            self.lastY = y
            self.canvas.after(15, self.updateOffset)

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

    def clearHandler(self):

        if self.massCount:
            for x in self.masses:
                self.canvas.delete(x.visualId)

            self.masses.clear()
            self.updateMassCount()
            
        self.xOffset = 0.0
        self.yOffset = 0.0
        self.scale = 1.0
        self.timeScale = 1.0
        self.timeStr.set("Time: 1.0x")
        self.timeSlider.set(10)
        self.play = True
        self.playHandler()

    def framesCallback(self):
        currentTime = time()
        deltaTime = currentTime - self.framesTime
        self.framesStr.set(f"FPS: {self.frames/deltaTime:.1f}")
        self.frames = 0
        self.framesTime = currentTime
        self.canvas.after(1000, self.framesCallback)
            

class Mass:
    def __init__(self, main:Simulator, vi:list=None) -> None:
        self.main = main
        self.mass = main.mass 
        self.size = 10 * math.log(self.mass + 250) - 30.21461

        # screen to world coordinates
        self.x = self.main.initial[0] / self.main.scale - self.main.xOffset
        self.y = self.main.initial[1] / self.main.scale - self.main.yOffset

        self.deltaV = [0.0, 0.0]
        if vi == None:
            self.vi = [0.0, 0.0]
        else: 
            self.vi = vi
        self.P = [(self.vi[0] * self.mass), (self.vi[1] * self.mass)] # momentum as (Px, Py)
        self.AG = [0.0, 0.0] # Acceleration due to gravity in (AGx, AGy) format

        self.visualId = self.main.canvas.create_oval(self.x - self.size, self.y - self.size, \
                                                     self.x + self.size, self.y + self.size, \
                                                     fill="black", outline="black")

        
    def updateAG(self) -> int:
        notPast = True
        self.AG[0] = 0.0
        self.AG[1] = 0.0

        for i in self.main.masses:
            if notPast and self is i: #made confusing for short circuit
                notPast = False #skips calculating gravity when self is x
                continue # also skips checking if self is x if notPast == False
            
            else:   #calculate acceleration to another body
                deltaX = i.x - self.x + 1e-15   # yeah, it's off by a hair, so what
                deltaY = i.y - self.y + 1e-15

                #TODO:handle division by zero before it happens
                if not deltaX:
                    print("This shouldn't be possible, deltaX = 0") # actually it is, just improbable
                    print(id(self))
                    print(id(i))
                    exit() #no you dont get to continue

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

        self.x = cm[0]
        self.y = cm[1]

        self.vi = vf
        


if __name__ == "__main__": 
    sim = Simulator()