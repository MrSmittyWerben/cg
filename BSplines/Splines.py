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

        # weight
        self.weightedPoints = []
        self.changeWeight = False
        self.currentPoint = None

        self.k = 4  # Degree
        self.m = 20  # Points to calculate per interval, default value

        self.drawCurve = False  # toggle when curve is ready
        self.drawControlPolygon = True  # toggle to set visibility of controlpoints / polygon

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
        if self.drawControlPolygon:
            glDrawArrays(GL_POINTS, 0, len(self.controlPoints))  # draw points
            if len(self.controlPoints) > 1:
                glDrawArrays(GL_LINE_STRIP, 0, len(self.controlPoints))
        pointData.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)

        if self.drawCurve:
            glColor(self.colors['RED'])
            curveData = vbo.VBO(np.array(self.curvePoints, 'f'))
            curveData.bind()
            glVertexPointer(2, GL_FLOAT, 0, curveData)
            glEnableClientState(GL_VERTEX_ARRAY)
            glDrawArrays(GL_POINTS, 0, len(self.curvePoints))  # draw curve
            if len(self.curvePoints) > 2:
                glColor(self.colors['BLUE'])
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

    def setPoint(self, x, y, weight=1.0):
        y = self.height - y  # translate y to our window
        self.weightedPoints.append(np.array([x * weight, y * weight, weight]))
        print(f"Controlpoint set at ({x}, {y}) with weight of {weight}")
        self.controlPoints.append(np.array([x, y]))  # y starts at the top
        if len(self.controlPoints) > (self.k - 1):
            self.k += 1
            self.setVector()
            self.calcCurve()

    def calcR(self, t):
        for i in range(len(self.knotVector)):
            if self.knotVector[i] > t:  # interval of t*
                return i - 1

    def deboor(self, degree, controlpoints, knotvector, t, r):
        if degree == 0:
            if r == len(controlpoints):
                return controlpoints[r - 1]
            else:
                return controlpoints[r]  # exit

        alpha = 0
        if knotvector[r] != knotvector[r - degree + self.k]:  # catch div by 0
            alpha = (t - knotvector[r]) / (knotvector[r - degree + self.k] - knotvector[r])

        return ((1 - alpha) * self.deboor(degree - 1, controlpoints, knotvector, t, r - 1)) + \
               (alpha * self.deboor(degree - 1, controlpoints, knotvector, t, r))

    def calcCurve(self):
        self.curvePoints.clear()
        t = 0
        while t < self.knotVector[-1]:  # while t is in vector
            r = self.calcR(t)
            curvePoint = self.deboor(self.k - 1, self.weightedPoints, self.knotVector, t, r)
            self.curvePoints.append(
                np.array([curvePoint[0] / curvePoint[2], curvePoint[1] / curvePoint[2]]))  # persp. div
            t += self.knotVector[-1] / float(self.m)  # step
        self.drawCurve = True

    def clearAll(self):
        self.controlPoints.clear()
        self.weightedPoints.clear()
        self.curvePoints.clear()


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
        glfw.set_cursor_pos_callback(self.window, self.onMouseMoved)

        # create 3D
        self.scene = Scene(self.width, self.height)

        # exit flag
        self.exitNow = False

    def onMouseMoved(self, win, x, y):
        if self.scene.changeWeight:
            y = self.height - y
            point_height = self.scene.controlPoints[self.scene.currentPoint][1]
            offset = y - point_height
            inc = offset / 500.0
            new_weight = 1
            if offset > 0:
                new_weight = (self.scene.weightedPoints[self.scene.currentPoint][2] + inc) if \
                    self.scene.weightedPoints[self.scene.currentPoint][2] <= 10 else 10

            if offset < 0:
                new_weight = (self.scene.weightedPoints[self.scene.currentPoint][2] + inc) if \
                    self.scene.weightedPoints[self.scene.currentPoint][2] > 1 else 1

            oldpoints = self.scene.weightedPoints.copy()
            print("Old: ", oldpoints)
            self.scene.weightedPoints.clear()

            for i in range(0, len(oldpoints)):
                if i != self.scene.currentPoint:
                    self.scene.weightedPoints.append(oldpoints[i])
                else:
                    p = np.array([self.scene.controlPoints[i][0], self.scene.controlPoints[i][1], 1])
                    self.scene.weightedPoints.append(p*new_weight)
            print("New: ", self.scene.weightedPoints)
            self.scene.calcCurve()

    def onMouseButton(self, win, button, action, mods):
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(win)
                y = self.height - y
                for i in range(0, len(self.scene.controlPoints)):
                    point = self.scene.controlPoints[i]
                    if (point[0] - 15 < x < point[0] + 15) and (point[1] - 15 < y < point[1] + 15):
                        self.scene.currentPoint = i
                        self.scene.changeWeight = True
                        break
            if action == glfw.RELEASE:
                self.scene.changeWeight = False

        elif button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(win)
                self.scene.setPoint(x, y)

    def onKeyboard(self, win, key, scancode, action, mods):
        # print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            if key == glfw.KEY_M:
                if mods == glfw.MOD_CAPS_LOCK or mods == glfw.MOD_SHIFT:
                    self.scene.m += 1
                else:
                    if self.scene.m != 1:  # limit
                        self.scene.m -= 1
                print(f"m is now {self.scene.m}")
                self.scene.calcCurve()

            if key == glfw.KEY_K:
                if mods == glfw.MOD_CAPS_LOCK or mods == glfw.MOD_SHIFT:
                    if self.scene.k < len(self.scene.controlPoints):
                        self.scene.k += 1
                else:
                    if self.scene.k != 1:
                        self.scene.k -= 1
                print(f"k is now {self.scene.k}")
                self.scene.setVector()
                self.scene.calcCurve()

            if key == glfw.KEY_C:
                self.scene.clearAll()
                print("Points cleared")

            if key == glfw.KEY_D:
                self.scene.drawControlPolygon = not self.scene.drawControlPolygon
                if self.scene.drawControlPolygon:
                    print("Visbility of control Polygon is set to on")
                else:
                    print("Visbility of control Polygon is to off")

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
