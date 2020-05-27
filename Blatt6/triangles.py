from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
import sys


points = []
originTri = [[0.0, 0.0], [0.1, 0.2], [0.2, 0.0]]
points.extend(originTri)

for i in range(2):
    copy = originTri.copy()

    p0 = copy[2]
    p1_0 = copy[1][0] + 0.2
    p1_1 = copy[1][1]
    p2_0 = copy[2][0] + 0.2
    p2_1 = copy[2][1]

    tri = [p0, [p1_0, p1_1], [p2_0, p2_1]]
    print(tri)
    points.extend(tri)

    originTri = tri

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
    glDrawArrays(GL_TRIANGLES, 0, 6)
    vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glFlush()


def main():
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow("triangles")

    glutDisplayFunc(display)
    initGL(500, 500)  # initialize OpenGL state
    glutMainLoop()  # start even processing


if __name__ == '__main__':
    main()