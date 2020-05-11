import numpy as np

from Raytracing.Ray import Ray

class Camera(object):
    def __init__(self, e, c, up, fov, imgWidth, imgHeight):
        self.e = e
        self.c = c
        self.up = up
        self.aspect_ratio = imgWidth/imgHeight

        self.fov = fov
        self.alpha = self.fov/2

        self.f = (self.c - self.e)/np.linalg.norm(self.c-self.e)
        self.s = np.cross(self.f,self.up)/np.linalg.norm(np.cross(self.f, self.up))
        self.u = np.cross(self.s, self.f) * (-1) # so it's not upside down
        self.height = 2*np.tan(self.alpha)
        self.width = self.aspect_ratio * self.height
        self.wRes = imgWidth
        self.hRes = imgHeight
        self.pixelWidth = self.width / (self.wRes-1)
        self.pixelHeight = self.height / (self.hRes-1)

    def calcRay(self, x,y):
        xcomp = self.s * (x*self.pixelWidth - self.width/2)
        ycomp = self.u * (y*self.pixelHeight - self.height/2)
        return Ray(self.e, self.f + xcomp + ycomp)