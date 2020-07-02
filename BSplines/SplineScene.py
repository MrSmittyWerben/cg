
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import numpy as np


class SplineScene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, width, height):
        self.pointsize = 5.0
        self.linewidth = 1.0
        self.width = width
        self.height = height
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)

        # movement
        self.doMove = False
        self.zoomFactor = 1.0

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

        self.actColor = 0.0, 0.0, 0.0, 0.0
        self.actBgColor = 1.0, 1.0, 1.0, 1.0

        self.controlPoints = []

    # render
    def render(self, width, height):

        glClearColor(*self.actBgColor)
        glColor(self.actColor)

        data = vbo.VBO(np.array(self.controlPoints, 'f'))
        data.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, data)
        glScale(self.zoomFactor, self.zoomFactor, self.zoomFactor)
        glDrawArrays(GL_POINTS, 0, int(len(self.controlPoints)/2))
        if len(self.controlPoints) > 1:
            glDrawArrays(GL_LINE_STRIP, 0, int(len(self.controlPoints)/2))
        data.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glFlush()

    def setPoint(self, x, y):
        self.controlPoints.extend((x, self.height-y))
        print(self.controlPoints)
