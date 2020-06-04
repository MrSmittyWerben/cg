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
        self.showVector = True
        self.pointsize = 3
        self.width = width
        self.height = height
        self.objFile = objFile
        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

        self.triangles, self.norms = Triangles(self.objFile).generateObj()

        # bounding box
        self.max_coords = np.maximum.reduce([p for p in self.triangles])
        self.min_coords = np.minimum.reduce([p for p in self.triangles])

        self.center = (self.max_coords + self.min_coords) / 2.0
        self.scale = 2.0 / np.amax(self.max_coords - self.min_coords)
        print('Center: ', self.center)

        self.points = []

        for (v, vn) in zip(self.triangles, self.norms):
            self.points.extend(v)
            self.points.extend(vn)

        self.data = vbo.VBO(np.array(self.points, 'f'))

    # render
    def render(self):

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)

        glColor3f(.75, .75, .75)

        # clear
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.data.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, self.data)
        glNormalPointer(GL_FLOAT, 24, self.data+12)

        #gluLookAt(0,0,4, 0,0,0, 0,1,0)

        glScale(self.scale, self.scale, self.scale)
        glTranslate(-self.center[0], -self.center[1], -self.center[2])

        #glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(self.triangles))
        self.data.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

        glFlush()
