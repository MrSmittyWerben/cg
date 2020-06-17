import math

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np

from Blatt8.objReaderTexture import Triangles


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

        # Polygonmode
        self.wireMode = False

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
        self.ambient = [0.0, 1.0, 1.0, 1.0]
        self.diffuse = [1.0, 1.0, 1.0, 0.6]
        self.specular = [1.0, 1.0, 1.0, 0.2]
        self.shiny = 70
        self.p = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 1 / (-self.light[1]), 0, 0]
        ]).transpose()

        # object
        self.triangles, self.norms, self.textures = Triangles(self.objFile).generateObj()

        # perspective
        self.perspective = False

        # bounding box
        self.max_coords = np.maximum.reduce([p for p in self.triangles])
        self.min_coords = np.minimum.reduce([p for p in self.triangles])

        self.center = (self.max_coords + self.min_coords) / 2.0

        self.scale = 2.0 / np.amax(self.max_coords-self.min_coords)

        scaledT = []
        for t in self.triangles:
            scaledT.append([t[0] * self.scale, t[1] * self.scale, t[2] * self.scale])

        self.triangles = scaledT

        self.points = []

        for v, vn in zip(self.triangles, self.norms):
            self.points.extend(v)
            self.points.extend(vn)

        self.data = vbo.VBO(np.array(self.points, 'f'))

    # render
    def render(self, width, height):
        glClearColor(*self.actBgColor)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light)

        glEnable(GL_LIGHTING)
        glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient)
        glMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse)
        glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular)
        glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, self.shiny)

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        # Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.perspective:
            if width <= height:
                gluPerspective(45 * height/float(width), width/float(height), 0.1, 100)
            else:
                gluPerspective(45 * width/float(width), width/float(height), 0.1, 100)
            gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)
        else:
            # zF changed to 5 so shadow doesnt get cut off
            if width <= height:
                glOrtho(-1.5, 1.5,
                        -1.5 * height / width, 1.5 * height / width,
                        -5.0, 5.0)
            else:
                glOrtho(-1.5 * width / height, 1.5 * width / height,
                        -1.5, 1.5,
                        -5.0, 5.0)

        # Modelview
        glMatrixMode(GL_MODELVIEW)

        self.data.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 24, self.data)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 24, self.data + 12)

        glLoadIdentity()
        glTranslate(-self.center[0]*self.scale, -self.center[1]*self.scale, -self.center[2]*self.scale)
        glTranslate(-self.coords[0], -self.coords[1], 0)
        glMultMatrixf(np.dot(self.actOri, self.rotate(self.angle, self.axis)))  # arcball
        glScale(self.zoomFactor, self.zoomFactor, self.zoomFactor)

        if self.wireMode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if self.hasShadow:
            self.renderShadow(width, height)

        glColor(*self.actColor)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)

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
        e= np.array([ex, ey, ez])
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

    def orthogonalMatrix(self, d):

        p = np.array([
            [d, 0, 0, 0],
            [0, d, 0, 0],
            [0, 0, d, 0],
            [0, 0, -1, 0]
        ])

        return p

    def projectOnSpehre(self, x, y, r):
        x, y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y ** 2)
        z = np.sqrt(r * r - a)
        l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        return x / l, y / l, z / l

    def renderShadow(self, width, height):
        glPushMatrix()
        glDisable(GL_LIGHT0)
        glDisable(GL_DEPTH_TEST)
        glTranslate(self.light[0], self.light[1]-math.fabs(self.min_coords[1]*self.scale), self.light[2])
        glMultMatrixf(self.p)
        glTranslate(-self.light[0], -self.light[1] + math.fabs(self.min_coords[1]*self.scale), -self.light[2])
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.85)
        glDrawArrays(GL_TRIANGLES, 0, len(self.points))
        glPopMatrix()
