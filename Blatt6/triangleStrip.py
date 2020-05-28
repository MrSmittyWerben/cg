from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
import sys

points = []
originTri = [[0.0, 0.0], [0.1, 0.2], [0.2, 0.0]]
points.extend(originTri)
points.extend([[.3,.2], [.4, 0], [.5, .2], [.6, 0], [.5, .2], [.7, .2], [.6, .4], [.8, .4], [.7, .2], [.8, .4], [.9, .2], [1, .4], [1.1, .2], [1.2, .4]])

'''
for i in range(14):
    flipped = False

    if i == 4 or i == 8 or i == 10:
        p_x = points[-2][0]
        p_y = points[-2][1]

    elif i == 5 or i == 7 or i == 9:
        p_x = points[-1][0] + 0.2
        p_y = points[-1][1]

    elif i == 6:
        p_x = points[-1][0] - 0.1
        p_y = points[-1][1] + 0.2

    else:
        p_x = points[-2][0] + 0.2
        p_y = points[-2][1]

    print(points)
    print(i, p_x,p_y)
    points.append([p_x, p_y])
'''


print(points)

vbo = vbo.VBO(array(points, 'f'))


def initGL(width, height):
    """ Initialize an OpenGL window """
    glClearColor(0.0, 0.0, 1.0, 0.0)  # background color
    glMatrixMode(GL_PROJECTION)  # switch to projection matrix
    glLoadIdentity()  # set to 1
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)  # multiply with new p-matrix
    glMatrixMode(GL_MODELVIEW)  # switch to modelview matrix


def display():
    """ Render all objects"""
    glClear(GL_COLOR_BUFFER_BIT)  # clear screen
    glColor3f(0.75, 0.75, 0.75)  # render stuff
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    vbo.bind()
    glVertexPointerf(vbo)
    glEnableClientState(GL_VERTEX_ARRAY)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, len(points))
    vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glFlush()


def main():
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow("Triangle Strip")

    glutDisplayFunc(display)
    initGL(500, 500)  # initialize OpenGL state
    glutMainLoop()  # start even processing


if __name__ == '__main__':
    main()