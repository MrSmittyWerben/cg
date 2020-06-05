import numpy as np


class Triangles(object):
    def __init__(self, file):
        self.v = []  # vertices
        self.vn = []  # normal coordinates
        self.vt = []  # texture coordinates
        self.f = []  # faces

        self.triangles = []
        self.normals = []
        self.textures = []

        self.hasNormals = False

        f = open(file)
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                v1 = float(parts[1])
                v2 = float(parts[2])
                v3 = float(parts[3])
                self.v.append((v1, v2, v3))

            if line.startswith("vn "):
                self.hasNormals = True
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

        for f in self.f:
            faces = []
            for point in f:
                if '/' in point:
                    parts = point.split('/')
                    faces.append([int(parts[0]), 0 if parts[1] == '' else int(parts[1]),
                                  0 if parts[2] == '' else int(parts[2])])  # v/vt/vn
                else:
                    faces.append([int(point), 0, 0])

            v1 = self.v[faces[0][0] - 1]
            v2 = self.v[faces[1][0] - 1]
            v3 = self.v[faces[2][0] - 1]

            arr1 = [v1[0], v1[1], v1[2]]
            arr2 = [v2[0], v2[1], v2[2]]
            arr3 = [v3[0], v3[1], v3[2]]
            self.triangles.extend([arr1, arr2, arr3])

            if faces[0][1] != 0:
                vt1 = self.vt[faces[0][1] - 1]
                vt2 = self.vt[faces[1][1] - 1]
                vt3 = self.vt[faces[2][1] - 1]
            else:
                vt1, vt2, vt3 = [0, 0, 0], [0, 0, 0], [0, 0, 0]

            arr1 = [vt1[0], vt1[1], vt1[2]]
            arr2 = [vt2[0], vt2[1], vt2[2]]
            arr3 = [vt3[0], vt3[1], vt3[2]]
            self.textures.extend([arr1, arr2, arr3])

            if faces[0][2] != 0:
                self.hasNormals = True
                vn1 = self.vn[faces[0][2] - 1]
                vn2 = self.vn[faces[1][2] - 1]
                vn3 = self.vn[faces[2][2] - 1]

                arr1 = [vn1[0], vn1[1], vn1[2]]
                arr2 = [vn2[0], vn2[1], vn2[2]]
                arr3 = [vn3[0], vn3[1], vn3[2]]
                self.normals.extend([arr1, arr2, arr3])

            else:
                self.hasNormals = False
                self.normals.extend([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        if not self.hasNormals:
            calcedNorms = self.calcNorm()

        #  no texture anyway for our points
        return self.triangles, self.normals

    def calcNorm(self):

        out = {tuple(vert): (0, 0, 0) for vert in self.v}

        for i in range(0, len(self.triangles), 3):
            v1 = np.array(self.triangles[i + 1]) - np.array(self.triangles[i])
            v2 = np.array(self.triangles[i + 2]) - np.array(self.triangles[i])
            n = np.cross(v1, v2)
            n = n / np.linalg.norm(n)
            out[tuple(self.triangles[i])] = out[tuple(self.triangles[i])] + n
            out[tuple(self.triangles[i + 1])] = out[tuple(self.triangles[i + 1])] + n
            out[tuple(self.triangles[i + 2])] = out[tuple(self.triangles[i + 2])] + n

        return list(out.values())


if __name__ == '__main__':
    obj = Triangles('cow.obj').generateObj()
