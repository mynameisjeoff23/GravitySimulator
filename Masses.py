import numpy as np
from Mass import Mass
from tkinter import Canvas

class Masses:

    G_CONST = 6.674215e-11

    def __init__(self, canvas:Canvas):

        self.masses = list[Mass]()
        self.canvas = canvas
        
    def addMass(self, mass:Mass):
        
        self.masses.append(mass)
        if len(self.masses) > 1:
            self.massArr =      np.append(self.massArr, mass.mass)
            self.sizes =        np.append(self.sizes, mass.size)
            self.positions =    np.append(self.positions, [[mass.x, mass.y]], axis=0)
            self.deltaV =       np.append(self.deltaV, [mass.deltaV], axis=0)
            self.P =            np.append(self.P, [mass.P], axis=0)
            self.AG =           np.append(self.AG, [mass.AG], axis=0)
        
        else:
            self.massArr =      np.array([x.mass for x in self.masses])
            self.sizes =        np.array([x.size for x in self.masses]) 
            self.positions =    np.array([[x.x, x.y] for x in self.masses])
            self.deltaV =       np.array([x.deltaV for x in self.masses])
            self.P =            np.array([x.P for x in self.masses])
            self.AG =           np.array([x.AG for x in self.masses])
        
    def removeMass(self, index):
        # unused to this day
        self.masses.pop(index)

        # and undeveloped, too
        self.massArr = np.array([x.mass for x in self.masses])
        self.sizes = np.array([x.size for x in self.masses]) 
        self.positions = np.array([[x.x, x.y] for x in self.masses])
        self.deltaV = np.array([x.deltaV for x in self.masses])
        self.P = np.array([x.P for x in self.masses])
        self.AG = np.array([x.AG for x in self.masses])

    def clear(self):
        self.masses.clear()

        del self.massArr    
        del self.positions  
        del self.deltaV     
        del self.P          
        del self.AG         

    def updateAG(self):
        #self.AG.fill(0.0) # probably don't need to do this
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
                    print("you suck lmao") # should not be possible (see lines 66 and 69)
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

    def collide(self, idx1:int, idx2:int):

        cm = [0.0, 0.0]
        mass1 = self.massArr[idx1]
        mass2 = self.massArr[idx2]

        #cm = (m1x1 + m2x2)/(m1 + m2)
        mTot = mass1 + mass2
        cm[0] = (mass1 * self.positions[idx1][0] + mass2 * self.positions[idx2][0])/(mTot)
        cm[1] = (mass1 * self.positions[idx1][1] + mass2 * self.positions[idx2][1])/(mTot)

        # m1v1 + m2v2 = mfvf
        pSys = [(self.P[idx1][0] + self.P[idx2][0]), (self.P[idx1][1] + self.P[idx2][1])]

        # vf = (m1v1 + m2v2)/mf
        vf = [(pSys[0]/(mTot)), (pSys[1]/(mTot))]

        if mass1 < mass2:
            #remove object 1 from all memory
            self.masses[idx2].afterCollision(mTot, vf, cm)
            self.canvas.delete(self.masses[idx1].visualId)
            self.removeMass(idx1)
        else: 
            #remove object 2 from all memory
            self.masses[idx1].afterCollision(mTot, vf, cm)
            self.canvas.delete(self.masses[idx2].visualId)
            self.removeMass(idx1)

if __name__ == "__main__":
    print("Use GravitySimulator.py to run the simulation")
    input("Press Enter to exit")
