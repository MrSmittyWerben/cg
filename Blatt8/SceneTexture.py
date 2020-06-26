import math

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np
from PIL import Image

from Blatt8.objReaderTexture import Triangles


class Scene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, objFile, shader, width, height):
        # time
        self.t = 0
        self.pointsize = 3
        self.width = width
        self.height = height
        self.objFile = objFile
        self.program = shader
        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

        # Colors
        self.red = 1.0, 0.0, 0.0, 1.0
        self.green = 0.0, 1.0, 0.0, 1.0
        self.blue = 0.0, 0.0, 1.0, 1.0
        self.yellow = 1.0, 1.0, 0.0, 1.0
        self.white = 1.0, 1.0, 1.0, 1.0
        self.black = 0.0, 0.0, 0.0, 1.0

        self.colors = {
            'RED': self.red,
            'GREEN': self.green,
            'BLUE': self.blue,
            'YELLOW': self.yellow,
            'WHITE': self.white,
            'BLACK': self.black
        }

        self.bgColors = {
            'RED': self.red,
            'GREEN': self.green,
            'BLUE': self.blue,
            'YELLOW': self.yellow,
            'WHITE': self.white,
            'BLACK': self.black
        }

        self.actColor = 0.75, 0.75, 0.75, 1.0
        self.actBgColor = 1.0, 1.0, 1.0, 1.0

        # Polygonmode
        self.wireMode = False
        self.solidMode = True
        self.pointMode = False

        # Rotation
        self.startP = 0
        self.moveP = 0
        self.doRotation = False
        self.axis = np.array([1, 1, 0])
        self.angle = 0
        self.actOri = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # movement
        self.doMove = False
        self.coords = (0, 0)

        # zoom
        self.zoomFactor = 1

        # shadows
        self.hasShadow = False
        self.light = [30, 30, 30]
        self.diffuse = [0.7059, 0.3922, 0.2353, 1]
        self.ambient = [0.1765, 0.0980, 0.0588, 1]
        self.specular = [0.3529, 0.1961, 0.1176, 1]
        self.shiny = 70
        self.p = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 1 / (-self.light[1]), 0, 0]
        ]).transpose()

        # texture
        self.getTexture("Squirreltexture.jpg")

        # object
        self.triangles, self.norms, self.textures = Triangles(self.objFile).generateObj()

        # bounding box
        self.max_coords = np.maximum.reduce([p for p in self.triangles])
        self.min_coords = np.minimum.reduce([p for p in self.triangles])

        self.center = (self.max_coords + self.min_coords) / 2.0

        self.scaleFactor = 2.0 / np.amax(self.max_coords-self.min_coords)

        '''
        scaledT = []
        for t in self.triangles:
            scaledT.append([t[0] * self.scale, t[1] * self.scale, t[2] * self.scale])

        self.triangles = scaledT
        '''

        self.points = []

        for v, vt, vn in zip(self.triangles, self.textures, self.norms):
            self.points.extend(v)
            self.points.extend(vt)
            self.points.extend(vn)

        self.data = vbo.VBO(np.array(self.points, 'f'))

        self.pMatrix = self.perspectiveMatrix(45, self.width/float(self.height), 0.1, 100)


    # render
    def render(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.actBgColor)

        mvMat = self.lookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)
        mvMat *= (self.rotate(self.angle, self.axis) * self.actOri)
        mvMat *= self.scale(self.scaleFactor * self.zoomFactor, self.scaleFactor * self.zoomFactor,
                            self.scaleFactor * self.zoomFactor)
        mvMat *= self.translate(-self.center[0] + self.coords[0], -self.center[1] + self.coords[1], - self.center[2])

        normalMat = np.linalg.inv(mvMat[0:3, 0:3]).transpose()
        mvpMat = self.pMatrix * mvMat

        glUseProgram(self.program)
        self.sendMat4("mvMatrix", mvMat)
        self.sendMat4("mvpMatrix", mvpMat)
        self.sendMat3("normalMatrix", normalMat)
        self.sendVec4("diffuseColor", self.diffuse)
        self.sendVec4("ambientColor", self.ambient)
        self.sendVec4("specularColor", self.specular)
        self.sendVec3("lightPosition", self.light)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        self.data.bind()

        glVertexPointer(3, GL_FLOAT, 32, self.data)
        glNormalPointer(GL_FLOAT, 32, self.data+12)
        glTexCoordPointer(2, GL_FLOAT, 32, self.data + 24)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(self.data))

        self.data.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)


    def sendValue(self, varName, value):
        varLocation = glGetUniformLocation(self.program, varName)
        glUniform1f(varLocation, value)

    def sendVec3(self, varName, value):
        varLocation = glGetUniformLocation(self.program, varName)
        glUniform3f(varLocation, *value)

    def sendVec4(self, varName, value):
        varLocation = glGetUniformLocation(self.program, varName)
        glUniform4f(varLocation, *value)

    def sendMat3(self, varName, matrix):
        varLocation = glGetUniformLocation(self.program, varName)
        glUniformMatrix3fv(varLocation, 1, GL_TRUE, matrix.tolist())

    def sendMat4(self, varName, matrix):
        varLocation = glGetUniformLocation(self.program, varName)
        glUniformMatrix4fv(varLocation, 1, GL_TRUE, matrix.tolist())

    def rotate(self, angle, axis):
        c, mc = np.cos(angle), 1 - np.cos(angle)
        s = np.sin(angle)
        l = np.sqrt(np.dot(axis, axis)) if np.sqrt(np.dot(axis, axis)) != 0.0 else 0.1
        x, y, z = axis / l

        r = np.array([
            [x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
            [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
            [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
            [0, 0, 0, 1]
        ])

        return r

    def translate(self, tx, ty, tz):
        t = np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])

        return t

    def scale(self, sx, sy, sz):
        s = np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])

        return s

    def normalize(self, array):
        l_array = np.linalg.norm(array)

        return array / l_array if l_array != 0 else array

    def lookAt(self, ex, ey, ez, cx, cy, cz, ux, uy, uz):
        e = np.array([ex, ey, ez])
        c = np.array([cx, cy, cz])
        up = np.array([ux, uy, uz])

        # normalize
        up = self.normalize(up)

        # view dir
        f = c - e
        f = self.normalize(f)

        # calc s
        s = np.cross(f, up)
        s = self.normalize(s)

        # calc u
        u = np.cross(s,f)

        l = np.array([
            [s[0], s[1], s[2], -np.dot(s,e)],
            [u[0], u[1], u[2], -np.dot(u, e)],
            [-f[0], -f[1], -f[2], -np.dot(f, e )],
            [0, 0, 0, 1]
        ])

        return l

    def perspectiveMatrix(self, fov, aspect, zN, zF):
        f = 1.0 / np.tan(fov/2.0)
        p = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (zF + zN)/(zN - zF), (2 * zF * zN)/(zN - zF)],
            [0, 0, -1, 0]
        ])

        return p


    def projectOnSpehre(self, x, y, r):
        x, y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y ** 2)
        z = np.sqrt(r * r - a)
        l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        return x / l, y / l, z / l

    def getTexture(self, textureImage):
        image = Image.open(textureImage)

        imagedata = np.array(image)
        imagedata = imagedata[::-1, :]
        imagedata = imagedata.tostring()

        textureID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textureID)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 2048, 2048, 0, GL_RGB, GL_UNSIGNED_BYTE, imagedata)
