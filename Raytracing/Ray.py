import numpy as np
from Raytracing.normalizer import normalize

class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin # Aufpunkt
        self.direction = normalize(direction) #normalisierter Richtungsvektor

    def __repr__(self):
        return 'Ray(%s,%s)' %(repr(self.origin), repr(self.direction))

    def pointAtParameter(self,t):
        return self.origin + self.direction * t