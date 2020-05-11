import math
import numpy as np

from Raytracing.normalizer import normalize


class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def __repr__(self):
        return 'Sphere(%s,%s)' % (repr(self.center), repr(self.radius))

    def intersectionParameter(self, ray):
        co = self.center - ray.origin
        v = np.dot(co, ray.direction)
        discriminant = v*v - np.dot(co,co) + self.radius * self.radius
        if discriminant < 0:
            return 0
        else:
            return v-math.sqrt(discriminant)

    def normalAt(self,p):
        return normalize(p-self.center)

class Plane(object):
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normalize(normal)
        self.material = material

    def __repr__(self):
        return 'Plane(%s,%s)' % (repr(self.point), repr(self.normal))

    def intersectionParameter(self, ray):
        op = ray.origin - self.point
        a = np.dot(op, self.normal)
        b = np.dot(ray.direction, self.normal)
        if b:
            return -a/b
        else:
            return 0

    def normalAt(self,p):
        return self.normal

class Triangle(object):
    def __init__(self, a, b, c, material):
        self.a = a
        self.b = b
        self.c = c
        self.u = self.b - self.a
        self.v = self.c - self.a

        self.material = material

    def __repr__(self):
        return 'Triangle(%s,%s,%s)' % (repr(self.a), repr(self.b), repr(self.c))

    def intersectionParameter(self, ray):
        w = ray.origin - self.a
        dv = np.cross(ray.direction, self.v)
        dvu = np.dot(dv, self.u)
        if dvu == 0.0:
            return 0
        wu = np.cross(w, self.u)
        r = np.dot(dv, w) / dvu
        s = np.dot(wu, ray.direction) / dvu
        if 0<=r and r<=1 and 0<=s and s<=1 and r+s<=1:
            return np.dot(wu, self.v) / dvu
        else:
            return 0

    def normalAt(self,p):
        return normalize(np.cross(self.u, self.v))