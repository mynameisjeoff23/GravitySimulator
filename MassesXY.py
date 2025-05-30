import numpy as np
from Mass import Mass
from tkinter import Canvas

class Masses:

    G_CONST = 6.674215e-11

    def __init__(self, canvas:Canvas):

        self.masses = list[Mass]()
        self.canvas = canvas
        
    def addMass(self, initialXY:tuple[float, float], vi:list[float], scale:float, \
                xOffset:float, yOffset:float, mass:float):
        
        m = Mass(initialXY, vi, scale, xOffset, yOffset, self.canvas, mass)
        if len(self.masses) > 0:

            self.masses.append(m)
            self.massArr =      np.append(self.massArr, m.mass)
            self.sizes =        np.append(self.sizes, m.size)
            self.posX =         np.append(self.posX, m.x)
            self.posY =         np.append(self.posY, m.y)
            self.viX =          np.append(self.viX, m.vi[0])
            self.viY =          np.append(self.viY, m.vi[1])
            self.pX =           np.append(self.pX, m.P[0])
            self.pY =           np.append(self.pY, m.P[1])
            self.AGx =           np.append(self.AGx, m.AG[0])
            self.AGy =           np.append(self.AGy, m.AG[1])
        
        else:
            
            self.masses.append(m)
            self.massArr =      np.array([x.mass for x in self.masses])
            self.sizes =        np.array([x.size for x in self.masses]) 
            self.posX =         np.array([x.x for x in self.masses])
            self.posY =         np.array([x.y for x in self.masses])
            self.viX =          np.array([x.vi[0] for x in self.masses])
            self.viY =          np.array([x.vi[1] for x in self.masses])
            self.pX =           np.array([x.P[0] for x in self.masses])
            self.pY =           np.array([x.P[1] for x in self.masses])
            self.AGx =          np.array([x.AG[0] for x in self.masses])
            self.AGy =          np.array([x.AG[1] for x in self.masses])
        
    def removeMass(self, index:int):

        self.masses.pop(index)

        self.massArr =  np.array([x.mass for x in self.masses])
        self.sizes =    np.array([x.size for x in self.masses]) 
        self.posX =     np.array([x.x for x in self.masses])
        self.posY =     np.array([x.y for x in self.masses])
        self.viX =      np.array([x.vi[0] for x in self.masses])
        self.viY =      np.array([x.vi[1] for x in self.masses])
        self.pX =       np.array([x.P[0] for x in self.masses])
        self.pY =       np.array([x.P[1] for x in self.masses])
        self.AGx =      np.array([x.AG[0] for x in self.masses])
        self.AGy =      np.array([x.AG[1] for x in self.masses])

    def updateMasses(self):

        for x in range(len(self.masses)):

            m = self.masses[x]

            m.mass =    self.massArr[x]
            m.size =    self.sizes[x]
            m.x =       self.posX[x]
            m.y =       self.posY[x]
            m.vi[0] =   self.viX[x]
            m.vi[1] =   self.viY[x]
            m.P[0] =    self.pX[x]
            m.P[1] =    self.pY[x]
            m.AG[0] =   self.AGx[x]
            m.AG[1] =   self.AGy[x]

    def clear(self):

        self.canvas.delete("all")
        self.masses.clear()

        del self.massArr    
        del self.posX  
        del self.posY  
        del self.viX     
        del self.viY     
        del self.pX         
        del self.pY         
        del self.AGx        
        del self.AGy        

    def updatePos(self, deltaT:float, iterations:int):
        #self.AG.fill(0.0) # probably don't need to do this
        for x in range(iterations):
            for i in range(len(self.masses)):

                diffX = self.posX - self.posX[i]
                diffY = self.posY - self.posY[i]
                dist = np.sqrt(diffX**2 + diffY**2)
                diffX[i] = 1.0, 1.0
                diffY[i] = 1.0          # prevents division by zero and \
                dist[i] = 1.0           # results to index i \
                                        # will be discarded later on

                maxSize = np.maximum(self.sizes[i], self.sizes)
        
                collide = np.where(dist < maxSize, 1, 0)
                collide[i] = 0 # prevents collision with itself

                if 1 in collide: 

                    # find index of first element it collides with
                    # other collisions can be dealt with in another iteration
                    index = collide.view(np.True_).argmax() // collide.itemsize                                           

                    if index == i: 
                        print("you suck lmao") # should not be possible (see line 92)
                        exit()

                    self.collide(int(index), i)
                    self.AGx.fill(0.0) # discard this round of gravity calculations
                    self.AGy.fill(0.0)
                    break

                theta = np.abs(np.arctan(diffY/diffX)) # might raise division by zero warning #TODO: remove comment

                directionX = np.where(diffX < 0, -1, 1)
                directionY = np.where(diffY < 0, -1, 1)
                
                aMagnitude = Masses.G_CONST * self.massArr / (dist**2)
                aMagnitude[i] = 0.0 # now have acceleration to every other mass but not to itself

                aX = aMagnitude * np.cos(theta) * directionX # (a * cos(theta) * xdir) = ax
                aY = aMagnitude * np.sin(theta) * directionY # (a * sin(theta) * ydir) = ay

                self.AGx[i] = np.sum(aX)
                self.AGy[i] = np.sum(aY)

            deltaVx = self.AGx * deltaT
            deltaVy = self.AGy * deltaT
            self.posX += (self.viX * deltaT) + (0.5 * deltaVx * deltaT)
            self.posY += (self.viY * deltaT) + (0.5 * deltaVy * deltaT)
            self.viX += deltaVx
            self.viY += deltaVy
            self.pX = self.viX * self.massArr
            self.pY = self.viY * self.massArr

    def collide(self, idx1:int, idx2:int):

        cm = [0.0, 0.0]
        mass1 = self.massArr[idx1]
        mass2 = self.massArr[idx2]

        #cm = (m1x1 + m2x2)/(m1 + m2)
        #TODO: can probably be numpyified, low priority
        mTot = mass1 + mass2
        cm[0] = (mass1 * self.posX[idx1] + mass2 * self.posX[idx2])/(mTot)
        cm[1] = (mass1 * self.posY[idx1] + mass2 * self.posY[idx2])/(mTot)

        # m1v1 + m2v2 = mfvf
        pSys = [(self.pX[idx1] + self.pX[idx2]), (self.pY[idx1] + self.pY[idx2])]

        # vf = (m1v1 + m2v2)/mf
        vf = [(pSys[0]/(mTot)), (pSys[1]/(mTot))]

        if mass1 < mass2:

            self.masses[idx2].afterCollision(mTot, vf, cm)
            self.updateMasses()

            #remove object 1 from all memory
            self.canvas.delete(self.masses[idx1].visualId)
            self.removeMass(idx1)
        else: 

            self.masses[idx1].afterCollision(mTot, vf, cm)
            self.updateMasses()
            
            #remove object 2 from all memory
            self.canvas.delete(self.masses[idx2].visualId)
            self.removeMass(idx2)

if __name__ == "__main__":

    print("Use GravitySimulator.py to run the simulation")
    input("Press Enter to exit")
