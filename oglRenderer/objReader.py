import numpy as np


class Triangles(object):
    def __init__(self, file):
        self.v = []  # vertices
        self.vn = []  # normal coordinates
        self.vt = []  # texture coordinates
        self.f = []  # faces

        f = open(file)
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                v1 = float(parts[1])
                v2 = float(parts[2])
                v3 = float(parts[3])
                self.v.append((v1, v2, v3))

            if line.startswith("vn "):
                parts = line.split()
                v1 = float(parts[1])
                v2 = float(parts[2])
                v3 = float(parts[3])
                self.vn.append((v1, v2, v3))

            if line.startswith("vt "):
                parts = line.split()
                v1 = float(parts[1])
                v2 = float(parts[2])
                v3 = float(parts[3])
                self.v.append((v1, v2, v3))

            if line.startswith("f "):
                parts = line.split()
                f1 = str(parts[1])
                f2 = str(parts[2])
                f3 = str(parts[3])
                self.f.append((f1, f2, f3))

        f.close()

    def generateObj(self):
        triangles = []
        normals = []
        texture = []

        for f in self.f:
            faces = []
            for point in f:
                if '/' in point:
                    parts = point.split('/')
                    faces.append([int(parts[0]), 0 if parts[1] == '' else int(parts[1]), 0 if parts[2] == '' else int(parts[2])])  # v/vt/vn
                else:
                    faces.append([int(point), 0, 0])

            v1 = self.v[faces[0][0] - 1]
            v2 = self.v[faces[1][0] - 1]
            v3 = self.v[faces[2][0] - 1]

            if faces[0][1] != 0:
                vt1 = self.vt[faces[0][1] - 1]
                vt2 = self.vt[faces[1][1] - 1]
                vt3 = self.vt[faces[2][1] - 1]
            else:
                vt1, vt2, vt3 = [0, 0, 0], [0, 0, 0], [0, 0, 0]

            if faces[0][2] != 0:
                vn1 = self.vn[faces[0][2] - 1]
                vn2 = self.vn[faces[1][2] - 1]
                vn3 = self.vn[faces[2][2] - 1]
            else:
                vn1, vn2, vn3 = calcNorm(v1,v2,v3)

            arr1 = [v1[0], v1[1], v1[2]]
            arr2 = [v2[0], v2[1], v2[2]]
            arr3 = [v3[0], v3[1], v3[2]]
            triangles.extend([arr1, arr2, arr3])

            arr1 = [vn1[0], vn1[1], vn1[2]]
            arr2 = [vn2[0], vn2[1], vn2[2]]
            arr3 = [vn3[0], vn3[1], vn3[2]]
            normals.extend([arr1, arr2, arr3])

            arr1 = [vt1[0], vt1[1], vt1[2]]
            arr2 = [vt2[0], vt2[1], vt2[2]]
            arr3 = [vt3[0], vt3[1], vt3[2]]
            texture.extend([arr1, arr2, arr3])

        #  no texture anyway for our points
        return triangles, normals

def calcNorm(v1,v2,v3):
    l2 = []
    l3 = []

    for item1, item2 in zip(v2,v1):
        l2.append(item1-item2)

    for item1, item2 in zip(v3,v1):
        l3.append(item1-item2)

    normal = np.cross(l2, l3)
    normalized = normal / np.linalg.norm(normal)

    return normalized, normalized, normalized

if __name__ == '__main__':
    obj = Triangles('cow.obj').generateObj()
    print(obj[1])
