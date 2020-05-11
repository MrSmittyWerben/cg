import numpy as np
import math

from Raytracing.Color import Color


class Material:
    def __init__(self, color, shininessFactor=1, reflectionFactor=0.3):
        self.color = color
        self.shininessFactor = shininessFactor
        self.reflectionFactor = reflectionFactor

        self.ambientCoefficient = 1.0
        self.diffuseCoefficient = 0.6
        self.specularCoefficient = 0.2

    def baseColorAt(self, p):
        return self.color

    def calcColor(self, lightray, normal, ray, point):

        l = lightray.direction
        d = ray.direction
        n = normal
        lr = (l - 2 * n * np.dot(n, l))

        ca = self.baseColorAt(point)
        c_in = Color(50, 50, 50)  # Lichtintensität

        ka = self.ambientCoefficient
        kd = self.diffuseCoefficient
        ks = self.specularCoefficient

        dot_ln = np.dot(l, n)
        dot_lrd = np.dot(lr, -d) ** self.shininessFactor

        ambient = ka * ca

        if dot_ln > 0:
            diffuse = (kd * dot_ln * c_in)
            if dot_lrd > 0:
                specular = (ks * dot_lrd * c_in)
            else:
                specular = Color(0, 0, 0)
        else:
            diffuse = Color(0, 0, 0)
            specular = Color(0, 0, 0)

        c_out = ambient + diffuse + specular

        return c_out


class CheckerboardMaterial(Material):
    def __init__(self, shininessFactor=10, reflectionFactor=0):
        self.shininessFactor = shininessFactor
        self.reflectionFactor = reflectionFactor
        self.baseColor = Color(0, 0, 0)
        self.otherColor = Color(255, 255, 255)
        self.ambientCoefficient = 1.0
        self.diffuseCoefficient = 0.6
        self.specularCoefficient = 0.2
        self.checkSize = 1

    def baseColorAt(self, p):
        v = np.array(p)
        v * (1.0 / self.checkSize)
        if (int(math.fabs(v[0]) + 0.5) + int(math.fabs(v[1]) + 0.5) + int(math.fabs(v[2]) + 0.5)) % 2:
            return self.otherColor
        return self.baseColor
