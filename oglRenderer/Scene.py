import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np

from oglRenderer.objReader import Triangles


class Scene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, objFile, width, height):
        # time
        self.t = 0
        self.pointsize = 3
        self.width = width
        self.height = height
        self.objFile = objFile
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

        # Movement
        self.startP = 0
        self.moveP = 0
        self.doRotation = False
        self.axis = np.array([1, 0, 0])
        self.angle = 0.1
        self.actOri = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # object
        self.triangles, self.norms = Triangles(self.objFile).generateObj()

        # perspective
        self.perspective = False

        # bounding box
        self.max_coords = np.maximum.reduce([p for p in self.triangles])
        self.min_coords = np.minimum.reduce([p for p in self.triangles])

        self.center = (self.max_coords + self.min_coords) / 2.0
        self.scale = 2.0 / np.amax(self.max_coords - self.min_coords)

        self.points = []

        for v, vn in zip(self.triangles, self.norms):
            self.points.extend(v)
            self.points.extend(vn)

        self.data = vbo.VBO(np.array(self.points, 'f'))

    # render
    def render(self, width, height):

        # clear
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glClearColor(*self.actBgColor)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        # Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.perspective:
            gluPerspective(45, width/float(height), 0.1, 100)
            gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)  # wont affect glOrtho
        else:
            if width <= height:
                glOrtho(-1.5, 1.5,
                        -1.5 * height / width, 1.5 * height / width,
                        -1.0, 1.0)
            else:
                glOrtho(-1.5 * width / height, 1.5 * width / height,
                        -1.5, 1.5,
                        -1.0, 1.0)

        # Modelview
        glMatrixMode(GL_MODELVIEW)

        glColor(*self.actColor)

        self.data.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, self.data)
        glNormalPointer(GL_FLOAT, 24, self.data + 12)


        glLoadIdentity()
        glMultMatrixf(np.dot(self.actOri, self.rotate(self.angle, self.axis)))  # arcball
        glScale(self.scale, self.scale, self.scale)
        glTranslate(-self.center[0], -self.center[1], -self.center[2])

        # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(self.points))
        self.data.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glFlush()

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

        return r.transpose()

    def projectOnSpehre(self, x, y, r):
        x, y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y ** 2)
        z = np.sqrt(r * r - a)
        l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        return x / l, y / l, z / l
