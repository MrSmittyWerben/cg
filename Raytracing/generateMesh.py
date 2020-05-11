import numpy as np


class TriForce(object):
    def __init__(self, file):
        self.vertices = []
        self.faces = []

        f = open(file)
        for line in f:
            if line.startswith("v "):
                parts = line.split(" ")
                v1 = float(parts[1])
                v2 = float(parts[2])
                v3 = float(parts[3])
                self.vertices.append((v1, v2, v3))

            if line.startswith("f "):
                parts = line.split(" ")
                f1 = float(parts[1])
                f2 = float(parts[2])
                f3 = float(parts[3])
                self.faces.append((f1, f2, f3))

        f.close()


def generateTriangles(obj):
    triangles = []
    for f in obj.faces:
        f1 = int(f[0])
        f2 = int(f[1])
        f3 = int(f[2])

        v1 = obj.vertices[f1 - 1]
        v2 = obj.vertices[f2 - 1]
        v3 = obj.vertices[f3 - 1]

        arr1 = np.array([v1[0], v1[1], v1[2]])
        arr2 = np.array([v2[0], v2[1], v2[2]])
        arr3 = np.array([v3[0], v3[1], v3[2]])

        triangles.append((arr1, arr2, arr3))

    return triangles


def rotateY(angle):
    sin = np.sin(angle)
    cos = np.cos(angle)

    m = np.array([[cos, 0, sin], [0, 1, 0], [-sin, 0, cos]])
    m_inv = np.linalg.inv(m)

    return m, m_inv
