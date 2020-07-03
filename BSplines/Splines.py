import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
from OpenGL.arrays import vbo


class Scene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, width, height):
        self.pointsize = 5
        self.linewidth = 1
        self.width = width
        self.height = height
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)

        # Curve stuff
        self.controlPoints = []
        self.knotVector = []
        self.curvePoints = []

        self.k = 4  # Degree
        self.m = 10  # Points to calculate per interval, default value

        self.drawCurve = False  # toggle when curve is ready

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

        self.actBgColor = 1.0, 1.0, 1.0, 1.0
        self.actColor = 0.0, 0.0, 0.0, 0.0

    # render 
    def render(self):
        glClearColor(*self.actBgColor)
        glColor(self.actColor)

        pointData = vbo.VBO(np.array(self.controlPoints, 'f'))
        pointData.bind()
        glVertexPointer(2, GL_FLOAT, 0, pointData)
        glEnableClientState(GL_VERTEX_ARRAY)
        glDrawArrays(GL_POINTS, 0, len(self.controlPoints))  # draw points
        if len(self.controlPoints) > 1:
            glDrawArrays(GL_LINE_STRIP, 0, len(self.controlPoints))
        pointData.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)

        if self.drawCurve:
            curveData = vbo.VBO(np.array(self.curvePoints, 'f'))
            curveData.bind()
            glVertexPointer(2, GL_FLOAT, 0, curveData)
            glEnableClientState(GL_VERTEX_ARRAY)
            glDrawArrays(GL_POINTS, 0, len(self.curvePoints))  # draw points
            if len(self.curvePoints) > 1:
                glDrawArrays(GL_LINE_STRIP, 0, len(self.curvePoints))
            curveData.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)

        glFlush()

    def setVector(self):
        # K = (0,...,0,1,2,3,...,n-(k-1), n-(k-2),...,n-(k-2))
        #      k-times    sequence              k-times
        self.knotVector.clear()

        n = len(self.controlPoints)
        k = self.k

        self.knotVector.extend([0] * k)
        self.knotVector.extend([i for i in range(1, n - (k - 2))])  # -2 because of python range
        self.knotVector.extend([n - (k - 2)] * k)

    def setPoint(self, x, y):
        self.controlPoints.append(np.array([x, self.height - y]))  # y starts at the top
        if len(self.controlPoints) > (self.k - 1):
            self.setVector()
            self.calcCurve()

    def calcR(self, t):
        for i in range(len(self.knotVector)):
            if self.knotVector[i] > t:  # interval of t*
                return i-1

    def deboor(self, degree, controlpoints, knotvector, t, r):

        if degree == 0:
            if r == len(controlpoints):
                return controlpoints[r-1]
            else:
                return controlpoints[r]  # exit

        alpha = 0
        if knotvector[r] != self.knotVector[r-degree+self.k]:  # catch div by 0
            alpha = (t-self.knotVector[r]) / (self.knotVector[r-degree+self.k] - knotvector[r])

        return ((1-alpha) * self.deboor(degree-1, self.controlPoints, self.knotVector, t, r-1)) + \
               (alpha * self.deboor(degree-1, self.controlPoints, self.knotVector, t, r))

    def calcCurve(self):
        t = 0
        while t < self.knotVector[-1]:  # while t is in vector
            r = self.calcR(t)
            print(r)
            print(self.knotVector)
            self.curvePoints.append(self.deboor(self.k-1, self.controlPoints, self.knotVector, t, r))
            t += 1 / float(self.m)  # step


class RenderWindow:
    """GLFW Rendering window class"""

    def __init__(self):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # window hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)
        glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

        # make a window
        self.width, self.height = 800, 600
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "Splines", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)

        # create 3D
        self.scene = Scene(self.width, self.height)

        # exit flag
        self.exitNow = False

        # animation flag
        self.animation = True

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(win)
                self.scene.setPoint(x, y)

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            # COLORS
            if mods == glfw.MOD_SHIFT:  # shift pressed (background color)
                if key == glfw.KEY_S:  # black
                    self.scene.actBgColor = self.scene.colors['BLACK']
                if key == glfw.KEY_W:  # white
                    self.scene.actBgColor = self.scene.colors['WHITE']
                if key == glfw.KEY_R:  # red
                    self.scene.actBgColor = self.scene.colors['RED']
                if key == glfw.KEY_B:  # blue
                    self.scene.actBgColor = self.scene.colors['BLUE']
                if key == glfw.KEY_G:  # yellow
                    self.scene.actBgColor = self.scene.colors['YELLOW']

    def run(self):
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # clear
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # render scene
            self.scene.render()

            glfw.swap_buffers(self.window)
            # Poll for and process events
            glfw.poll_events()
        # end
        glfw.terminate()


# main() function
def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()


# call main
if __name__ == '__main__':
    main()
