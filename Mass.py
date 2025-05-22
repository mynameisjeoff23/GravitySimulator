from tkinter import Canvas as Canvas
from math import log
class Mass:
    
    def __init__(self, initialXY:tuple[float, float], vi:list[float], scale:float, xOffset:float, yOffset:float, \
                 canvas:Canvas, deltaT:float, mass:float):
        
        self.mass = mass
        self.size = 10 * log(self.mass + 250) - 30.21461

        self.x = initialXY[0] / scale - xOffset
        self.y = initialXY[1] / scale - yOffset

        self.deltaV = [0.0, 0.0]
        self.vi = vi
        self.P = [0.0, 0.0] # momentum as (Px, Py)
        self.AG = [0.0, 0.0] # Acceleration due to gravity in (AGx, AGy) format

        self.visualId = canvas.create_oval(self.x - self.size, self.y - self.size, \
                                                     self.x + self.size, self.y + self.size, \
                                                     fill="black", outline="black")
        
    def afterCollision(self, new:float, vf:list[float], cm:list[float]):
        
        self.mass = new
        self.size = 10 * log(self.mass + 250) - 30.21461

        self.x = cm[0]
        self.y = cm[1]

        self.vi = vf

if __name__ == "__main__":
    print("Use GravitySimulator.py to run the simulation")
    input("Press Enter to exit")        