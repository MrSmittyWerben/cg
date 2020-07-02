import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from BSplines.SplineScene import SplineScene


class RenderWin:
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
        self.window = glfw.create_window(self.width, self.height, "B-Splines", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_cursor_pos_callback(self.window, self.mouseMoved)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_scroll_callback(self.window, self.onScroll)

        # cursor position
        self.currentPosX = 0
        self.currentPosY = 0

        self.lastPosX = 0
        self.lastPosY = 0

        # create Scene
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.width, 0.0, self.height, 1.0, -1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.scene = SplineScene(self.width, self.height)

        # exit flag
        self.exitNow = False

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(win)
                self.scene.setPoint(x, y)

    def mouseMoved(self, window, x, y):

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

            ## OPTIONS

            if key == glfw.KEY_M:
                if mods == glfw.MOD_SHIFT or mods == glfw.MOD_CAPS_LOCK:
                    self.scene.renderCurvePoints += 1
                else:
                    self.scene.renderCurvePoints -= 1

            if key == glfw.KEY_K:
                if mods == glfw.MOD_SHIFT or mods == glfw.MOD_CAPS_LOCK:
                    self.scene.curveOrder += 1
                else:
                    self.scene.curveOrder -= 1


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
    rw = RenderWin()
    rw.run()


# call main
if __name__ == '__main__':
    main()
