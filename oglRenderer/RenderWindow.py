import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np

from oglRenderer.Scene import Scene
from oglRenderer.objReader import Triangles

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
        self.aspect = self.width/float(self.height)
        self.window = glfw.create_window(self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        
        # create 3D
        self.scene = Scene(objFile, self.width, self.height)

        # exit flag
        self.exitNow = False
    
    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

    def onSize(self, win, width, height):  # reshape
        print("onsize: ", win, width, height)
        # prevent division by zero
        if height == 0:
            height = 1

        self.width = width
        self.height = height
        self.aspect = width/float(height)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        if width <= height:
            glOrtho(-1.5, 1.5,
                    -1.5 * height / width, 1.5 * height / width,
                    -1.0, 1.0)
        else:
            glOrtho(-1.5 * width / height, 1.5 * width / height,
                    -1.5, 1.5,
                    -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)

    def run(self):

        while not glfw.window_should_close(self.window) and not self.exitNow:

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
        if sys.argv[1].lower() in ('bunny', 'cow', 'squirrel', 'elephant'):
            objFile = f"{sys.argv[1].lower()}.obj"
    else:
        sys.exit(-1)

    main()