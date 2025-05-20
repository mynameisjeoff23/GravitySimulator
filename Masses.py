import numpy as np
from Mass import Mass

class Masses:

    G_CONST = 6.674215e-11

    def __init__(self):

        self.masses = list[Mass]()
        
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
            self.massArr = np.array([x.mass for x in self.masses])
            self.sizes = np.array([x.size for x in self.masses]) 
            self.positions = np.array([[x.x, x.y] for x in self.masses])
            self.deltaV = np.array([x.deltaV for x in self.masses])
            self.P = np.array([x.P for x in self.masses])
            self.AG = np.array([x.AG for x in self.masses])
        
    def removeMass(self, mass:Mass):
        # unused to this day
        self.masses.remove(mass)

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

            maxSize = np.maximum(self.sizes[i], self.sizes)
            collide = np.where(dist < maxSize, 1, 0)
            #TODO: handle collisions later

            theta = np.abs(np.arctan(diff[ : , 1]/diff[ : , 0]))

            direction = np.where(diff < 0, -1, 1)

            a = Masses.G_CONST * self.massArr / (dist**2)
            a[i] = [0.0, 0.0] # now have acceleration to every other mass

            b = a[:]
            # a * cos(theta) * xdir
            b[:, 0] = a * np.cos(theta) * direction[:, 0]
            # a * sin(theta) * y dir
            b[:, 1] = a * np.sin(theta) * direction[:, 1]
            self.AG[i] = np.sum(b, axis=0)


