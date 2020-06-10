from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL import *
import sys, math, os
import numpy as np

EXIT = -1
FIRST = 0

WIDTH = 500
HEIGHT = 500
ASPECT = WIDTH/HEIGHT

# init global vars
pointList = []
max_coord = np.array([])
min_coord = np.array([])
center = np.array([])
scale = 1

ALPHA = 10
rotX, rotY, rotZ = 0, 0, 0

if len(sys.argv) != 2:
    print("oglViewer.py")
    sys.exit(-1)

elif sys.argv[1].lower() in ("bunny", "elephant", "squirrel", "cow"):

    filename = f"{sys.argv[1]}_points.raw"
    f = open(filename).readlines()
    for coords in f:
        x, y, z = coords.split()
        point = [float(x), float(y), float(z)]
        pointList.append(point)

    # bounding box
    max_coord = np.maximum.reduce([p for p in pointList])
    min_coord = np.minimum.reduce([p for p in pointList])
    center = (max_coord + min_coord) / 2.0
    scale = 2.0 / np.amax(max_coord-min_coord)

    vbo = vbo.VBO(np.array(pointList, 'f'))

else:
    print("Invalid args received")
    sys.exit(-1)


def init(width, height):
    """ Initialize an OpenGL window """
    glClearColor(0.0, 0.0, 0.0, 1.0)  # background color

    glMatrixMode(GL_PROJECTION)  # switch to projection matrix
    glLoadIdentity()  # set to 1
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)  # multiply with new p-matrix
    glMatrixMode(GL_MODELVIEW)  # switch to modelview matrix

def display():
    """ Render all objects"""
    glClear(GL_COLOR_BUFFER_BIT)  # clear screen
    glColor(1.0, 0.0, 0.0)  # render stuff

    glLoadIdentity()

    glRotate(rotX, 1, 0, 0)  # rotate x
    glRotate(rotY, 0, 1, 0)  # rotate y
    glRotate(rotZ, 0, 0, 1)  # rotate z

    glScale(scale, scale, scale)  # scale to window
    glTranslate(-center[0], -center[1], -center[2])

    vbo.bind()
    glVertexPointerf(vbo)
    glEnableClientState(GL_VERTEX_ARRAY)
    glDrawArrays(GL_POINTS, 0, len(pointList))
    vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)

    glutSwapBuffers()  # swap buffer


def reshape(width, height):
    """ adjust projection matrix to window size"""
    if height == 0:
        height = 1

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if width <= height:
        glOrtho(-1.5, 1.5,
                -1.5 * height / width, 1.5 * height / width,
                -1.0, 1.0)
    else:
        glOrtho(-1.5 * width / height, 1.5 * width / height,
                -1.5, 1.5,
                -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)


def keyPressed(key, x, y):
    global ALPHA, rotX, rotY, rotZ

    # Convert bytes object to string
    key = key.decode("utf-8")

    """ handle keypress events """

    print('Key pressed: ', key)
    if key == chr(27):  # chr(27) = ESCAPE
        sys.exit()

    if key == 'x':
        rotX += ALPHA

    if key == 'X':
        rotX -= ALPHA

    if key == 'y':
        rotY += ALPHA

    if key == 'Y':
        rotY -= ALPHA

    if key == 'z':
        rotZ += ALPHA

    if key == 'Z':
        rotZ -= ALPHA

    glutPostRedisplay()


def mouse(button, state, x, y):
    """ handle mouse events """
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print("left mouse button pressed at ", x, y)


def mouseMotion(x, y):
    """ handle mouse motion """
    print("mouse motion at ", x, y)


def menu_func(value):
    """ handle menue selection """
    print("menue entry ", value, "choosen...")
    if value == EXIT:
        sys.exit()
    glutPostRedisplay()


def main():
    # Hack for Mac OS X
    cwd = os.getcwd()
    glutInit(sys.argv)
    os.chdir(cwd)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow("simple openGL/GLUT template")

    glutDisplayFunc(display)  # register display function
    glutReshapeFunc(reshape)  # register reshape function
    glutKeyboardFunc(keyPressed)  # register keyboard function
    glutMouseFunc(mouse)  # register mouse function
    glutMotionFunc(mouseMotion)  # register motion function
    glutCreateMenu(menu_func)  # register menue function

    glutAddMenuEntry("First Entry", FIRST)  # Add a menu entry
    glutAddMenuEntry("EXIT", EXIT)  # Add another menu entry
    glutAttachMenu(GLUT_RIGHT_BUTTON)  # Attach mouse button to menue

    init(WIDTH, HEIGHT)  # initialize OpenGL state

    glutMainLoop()  # start even processing


if __name__ == "__main__":
    # Start
    main()
