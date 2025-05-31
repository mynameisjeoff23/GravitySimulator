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
            self.positions =    np.append(self.positions, [[m.x, m.y]], axis=0)
            self.vi =           np.append(self.vi, [m.vi], axis=0)
            self.P =            np.append(self.P, [m.P], axis=0)
            self.AG =           np.append(self.AG, [m.AG], axis=0)
        
        else:
            
            self.masses.append(m)
            self.massArr =      np.array([x.mass for x in self.masses])
            self.sizes =        np.array([x.size for x in self.masses]) 
            self.positions =    np.array([[x.x, x.y] for x in self.masses])
            self.vi =           np.array([x.vi for x in self.masses])
            self.P =            np.array([x.P for x in self.masses])
            self.AG =           np.array([x.AG for x in self.masses])
        
    def removeMass(self, index:int):

        self.masses.pop(index)

        self.massArr =      np.array([x.mass for x in self.masses])
        self.sizes =        np.array([x.size for x in self.masses]) 
        self.positions =    np.array([[x.x, x.y] for x in self.masses])
        self.vi =           np.array([x.vi for x in self.masses])
        self.P =            np.array([x.P for x in self.masses])
        self.AG =           np.array([x.AG for x in self.masses])

    def updateMasses(self):

        for x in range(len(self.masses)):

            m = self.masses[x]

            m.mass =    self.massArr[x]
            m.size =    self.sizes[x]
            m.x =       self.positions[x, 0]
            m.y =       self.positions[x, 1]
            m.vi[0] =   self.vi[x, 0]
            m.vi[1] =   self.vi[x, 1]
            m.P[0] =    self.P[x, 0]
            m.P[1] =    self.P[x, 1]
            m.AG[0] =   self.AG[x, 0]
            m.AG[1] =   self.AG[x, 1]

    def clear(self):

        self.canvas.delete("all")
        self.masses.clear()

        del self.massArr    
        del self.positions  
        del self.vi     
        del self.P          
        del self.AG         

    def updatePos(self, deltaT:float, iterations:int):
        #self.AG.fill(0.0) # probably don't need to do this
        for x in range(iterations):
            for i in range(len(self.masses)):

                diff = self.positions - self.positions[i]
                dist = np.sqrt(np.sum(diff**2, axis=-1))
                diff[i] = [1.0, 1.0]    # prevents division by zero and
                dist[i] = 1.0           # results to index i
                                        # will be discarded later on

                maxSize = np.maximum(self.sizes[i], self.sizes)
        
                collide = np.where(dist < maxSize, 1, 0)
                collide[i] = 0 # prevents collision with itself

                if 1 in collide: 

                    # find index of first element it collides with
                    # other collisions can be dealt with in another iteration
                    index = collide.view(np.True_).argmax() // collide.itemsize                                           

                    if index == i: 
                        print("you suck lmao") # should not be possible (see line 74)
                        exit()

                    self.collide(int(index), i)
                    self.AG.fill(0) # discard this round of gravity calculations
                    break

                theta = np.abs(np.arctan(diff[ : , 1]/diff[ : , 0])) # might raise division by zero warning #TODO: remove comment

                direction = np.where(diff < 0, -1, 1)
                
                aMagnitude = Masses.G_CONST * self.massArr / (dist**2)
                aMagnitude[i] = 0.0 # now have acceleration to every other mass but not to itself

                aVector = np.zeros((len(aMagnitude), 2))
                aVector[:, 0] = aMagnitude * np.cos(theta) * direction[:, 0] # (a * cos(theta) * xdir) = ax
                aVector[:, 1] = aMagnitude * np.sin(theta) * direction[:, 1] # (a * sin(theta) * ydir) = ay

                self.AG[i] = np.sum(aVector, axis=0)

            deltaV = self.AG * deltaT
            self.positions += (self.vi * deltaT) + (0.5 * deltaV * deltaT)
            self.vi += deltaV

            self.P[:, 0] = self.vi[:, 0] * self.massArr # cannot broadcast 1d and 2d\
            self.P[:, 1] = self.vi[:, 1] * self.massArr # array of same length

    def collide(self, idx1:int, idx2:int):

        cm = [0.0, 0.0]
        mass1 = self.massArr[idx1]
        mass2 = self.massArr[idx2]

        #cm = (m1x1 + m2x2)/(m1 + m2)
        #TODO: can probably be numpyified, low priority
        mTot = mass1 + mass2
        cm[0] = (mass1 * self.positions[idx1][0] + mass2 * self.positions[idx2][0])/(mTot)
        cm[1] = (mass1 * self.positions[idx1][1] + mass2 * self.positions[idx2][1])/(mTot)

        # m1v1 + m2v2 = mfvf
        pSys = [(self.P[idx1][0] + self.P[idx2][0]), (self.P[idx1][1] + self.P[idx2][1])]

        # vf = (m1v1 + m2v2)/mf
        vf = [(pSys[0]/(mTot)), (pSys[1]/(mTot))]

        if mass1 < mass2:

            self.vi[idx2] = vf
            self.massArr[idx2] = mTot
            self.positions[idx2] = cm

            #self.masses[idx2].afterCollision(mTot, vf, cm) # should not be necessary
            self.updateMasses()

            #remove object 1 from all memory
            self.canvas.delete(self.masses[idx1].visualId)
            self.removeMass(idx1)
        else: 
            self.vi[idx1] = vf
            self.massArr[idx1] = mTot
            self.positions[idx1] = cm

            #self.masses[idx1].afterCollision(mTot, vf, cm)
            self.updateMasses()
            
            #remove object 2 from all memory
            self.canvas.delete(self.masses[idx2].visualId)
            self.removeMass(idx2)

if __name__ == "__main__":

    print("Use GravitySimulator.py to run the simulation")
    input("Press Enter to exit")
