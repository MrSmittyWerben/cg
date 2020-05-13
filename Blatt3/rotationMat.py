import numpy as np


def readMat(mat1, mat2):
    f1 = open(mat1)
    parts = []
    for p in f1:
        res = p.split()
        for ele in res:
            parts.append(float(ele))

    matrix1 = np.array([
        [parts[0], parts[1], parts[2]],
        [parts[3], parts[4], parts[5]],
        [parts[6], parts[7], parts[8]]])

    f1.close()
    parts.clear()

    f2 = open(mat2)
    parts = []
    for p in f2:
        res = p.split()
        for ele in res:
            parts.append(float(ele))

    matrix2 = np.array([
        [parts[0], parts[1], parts[2]],
        [parts[3], parts[4], parts[5]],
        [parts[6], parts[7], parts[8]]])

    f2.close()

    return [matrix1, matrix2]


def checkRot(matrix):
    if np.allclose(np.linalg.inv(matrix), matrix.transpose()) and int(np.linalg.det(matrix)) == 1:
        return True
    return False


def getAngle(matrix):
    return int((np.arccos((np.trace(matrix) - 1) / 2)) * (180/np.pi))


def getAxis(matrix):
    v1 = matrix.item(2) * matrix.item(5) - (matrix.item(4) - 1) * matrix.item(2)
    v2 = matrix.item(3) * matrix.item(2) - (matrix.item(0) - 1) * matrix.item(5)
    v3 = (matrix.item(0) - 1) * (matrix.item(4) - 1) - matrix.item(1) * matrix.item(3)

    return np.array([v1, v2, v3])


if __name__ == '__main__':
    matrices = readMat("mat1.dat", "mat2.dat")
    for matrix in matrices:
        print(" %s \n" % matrix)
        if checkRot(matrix):
            print("Is a rotation matrix!\n")
            print("Angle: %s°" % getAngle(matrix))
            print("Axis: %s" % getAxis(matrix))
        else:
            print("Not a rotation matrix!\n")
