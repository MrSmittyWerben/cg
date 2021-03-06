import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np

from oglRenderer.Scene import Scene

global objFile, vbo


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

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_cursor_pos_callback(self.window, self.mouseMoved)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_scroll_callback(self.window, self.onScroll)

        # cursor position
        self.currentPosX = 0
        self.currentPosY = 0

        self.lastPosX = 0
        self.lastPosY = 0

        # create 3D
        self.scene = Scene(objFile, self.width, self.height)

        # exit flag
        self.exitNow = False

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)
        r = min(self.width, self.height) / 2.0
        ## Rotation
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(win)
                self.scene.doRotation = True
                self.scene.startP = self.scene.projectOnSpehre(x, y, r)
            elif action == glfw.RELEASE:
                self.scene.doRotation = False
                self.scene.actOri = np.dot(self.scene.actOri, self.scene.rotate(self.scene.angle, self.scene.axis))
                self.scene.angle = 0

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.scene.doMove = True
            elif action == glfw.RELEASE:
                self.scene.doMove = False

        ## Zoom
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            self.scene.zoomFactor += 0.1

    def mouseMoved(self, window, x, y):
        if self.scene.doRotation:
            r = min(self.width, self.height) / 2.0
            self.scene.moveP = self.scene.projectOnSpehre(x, y, r)
            dot = np.dot(self.scene.startP, self.scene.moveP)
            if dot < -1:  # arccos values must be between -1 and 1
                dot = -1
            if dot > 1:
                dot = 1
            self.scene.angle = np.arccos(dot)
            self.scene.axis = np.cross(self.scene.startP, self.scene.moveP)

        if self.scene.doMove:
            offX = x - self.lastPosX
            offY = y - self.lastPosY

            self.currentPosX -= 2 * offX/self.width  # division/multiplication to move more naturally
            self.currentPosY += 2 * offY/self.height

            self.scene.coords = (self.currentPosX, self.currentPosY)

        self.lastPosX = x
        self.lastPosY = y

    def onScroll(self, win, xOff, yOff):
        if self.scene.zoomFactor < 0.1:
            self.scene.zoomFactor = 0.1

        elif self.scene.zoomFactor > 2:
            self.scene.zoomFactor = 2

        else:
            self.scene.zoomFactor += 0.1 if yOff > 0 else -0.1  # zoom step

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            ## orthogonal <-> perspective
            if key == glfw.KEY_O:
                self.scene.perspective = False
                glfw.set_window_title(win, '2D Scene - Orthographic')

            if key == glfw.KEY_P:
                self.scene.perspective = True
                glfw.set_window_title(win, '2D Scene - Perspective')


            ## COLORS

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

            else:  # shift not pressed ( object color)
                if key == glfw.KEY_S:  # black
                    self.scene.actColor = self.scene.colors['BLACK']
                if key == glfw.KEY_W:  # white
                    self.scene.actColor = self.scene.colors['WHITE']
                if key == glfw.KEY_R:  # red
                    self.scene.actColor = self.scene.colors['RED']
                if key == glfw.KEY_B:  # blue
                    self.scene.actColor = self.scene.colors['BLUE']
                if key == glfw.KEY_G:  # yellow
                    self.scene.actColor = self.scene.colors['YELLOW']

                if key == glfw.KEY_H:  # shadows
                    self.scene.hasShadow = not self.scene.hasShadow

                if key == glfw.KEY_N:  # shadows
                    self.scene.wireMode = not self.scene.wireMode

    def onSize(self, win, width, height):  # reshape
        print("onsize: ", win, width, height)
        # prevent division by zero
        if height == 0:
            height = 1

        if width == 0:
            width = 1

        self.width = width
        self.height = height
        self.aspect = width / float(height)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.scene.perspective:
            if width <= height:
                gluPerspective(45*(height/float(width)), self.aspect, 0.1, 100)
            else:
                gluPerspective(45 * self.aspect, self.aspect, 0.1, 100)
            gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)

        else:
            if width <= height:
                glOrtho(-1.5, 1.5,
                        -1.5 * height / width, 1.5 * height / width,
                        -5.0, 5.0)
            else:
                glOrtho(-1.5 * width / height, 1.5 * width / height,
                        -1.5, 1.5,
                        -5.0, 5.0)

        glMatrixMode(GL_MODELVIEW)

    def run(self):

        while not glfw.window_should_close(self.window) and not self.exitNow:
            # clear
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.scene.render(self.width, self.height)

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

    if len(sys.argv) == 2:
        if sys.argv[1].lower() in ('bunny', 'cow', 'squirrel', 'squirrel2', 'elephant'):
            objFile = f"{sys.argv[1].lower()}.obj"
        else:
            print('Invalid arguments received!')
            sys.exit(-1)
    else:
        sys.exit(-1)

    main()
