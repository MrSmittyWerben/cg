import glfw
from OpenGL.GL.shaders import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np

from Blatt8.SceneTexture import Scene

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
        vertexShader = open('PhongShader.vert', 'r').read()
        fragmentShader = open('PhongShader.frag', 'r').read()
        self.program = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                      compileShader(fragmentShader, GL_FRAGMENT_SHADER))

        self.scene = Scene(objFile, self.program, self.width, self.height)
        self.scene.getTexture("Squirreltexture.jpg")
        print("done")

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

            self.currentPosX -= 2 * offX / self.width  # division/multiplication to move more naturally
            self.currentPosY += 2 * offY / self.height

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

            ## COLORS
            if mods == glfw.MOD_SHIFT:  # shift pressed (background color)
                # if key == glfw.KEY_S:  # black
                #    self.scene.actBgColor = self.scene.colors['BLACK']
                if key == glfw.KEY_W:  # white
                    self.scene.actBgColor = self.scene.colors['WHITE']
                if key == glfw.KEY_R:  # red
                    self.scene.actBgColor = self.scene.colors['RED']
                if key == glfw.KEY_B:  # blue
                    self.scene.actBgColor = self.scene.colors['BLUE']
                if key == glfw.KEY_G:  # yellow
                    self.scene.actBgColor = self.scene.colors['YELLOW']

            else:  # shift not pressed ( object color)
                # if key == glfw.KEY_S:  # black
                #      self.scene.actColor = self.scene.colors['BLACK']
                if key == glfw.KEY_W:  # white
                    self.scene.actColor = self.scene.colors['WHITE']
                if key == glfw.KEY_R:  # red
                    self.scene.actColor = self.scene.colors['RED']
                if key == glfw.KEY_B:  # blue
                    self.scene.actColor = self.scene.colors['BLUE']
                if key == glfw.KEY_G:  # yellow
                    self.scene.actColor = self.scene.colors['YELLOW']

            if key == glfw.KEY_W:
                self.scene.wireMode = True
                self.scene.solidMode = False
                self.scene.pointMode = False

            if key == glfw.KEY_S:
                self.scene.wireMode = False
                self.scene.solidMode = True
                self.scene.pointMode = False

            if key == glfw.KEY_P:
                self.scene.wireMode = False
                self.scene.solidMode = False
                self.scene.pointMode = True

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

        if width <= height:
            self.scene.pMatrix = self.scene.perspectiveMatrix(45 * height / float(width), self.aspect, 0.1, 100)
        else:
            self.scene.pMatrix = self.scene.perspectiveMatrix(45 * self.aspect, self.aspect, 0.1, 100)

    def run(self):

        while not glfw.window_should_close(self.window) and not self.exitNow:
            # clear
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

    if len(sys.argv) == 2:
        if sys.argv[1] == 'Squirrel':
            objFile = f"{sys.argv[1].lower()}Textured.obj"
        else:
            print('Invalid arguments received!')
            sys.exit(-1)
    else:
        sys.exit(-1)

    main()
