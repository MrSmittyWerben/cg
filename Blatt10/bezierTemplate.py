from tkinter import *
import sys

import numpy as np

WIDTH = 400  # width of canvas
HEIGHT = 400  # height of canvas

HPSIZE = 2  # half of point size (must be integer)
CCOLOR = "#0000FF"  # blue (color of control-points and polygon)

BCOLOR = "#000000"  # black (color of bezier curve)
BWIDTH = 2  # width of bezier curve

pointList = []  # list of (control-)points
elementList = []  # list of elements (used by Canvas.delete(...))

a = 0
b = 1
n = 1000


def drawPoints():
    """ draw (control-)points """
    for p in pointList:
        element = can.create_oval(p[0] - HPSIZE, p[1] - HPSIZE,
                                  p[0] + HPSIZE, p[1] + HPSIZE,
                                  fill=CCOLOR, outline=CCOLOR)
        elementList.append(element)


def drawPolygon():
    """ draw (control-)polygon conecting (control-)points """
    if len(pointList) > 1:
        for i in range(len(pointList) - 1):
            element = can.create_line(pointList[i][0], pointList[i][1],
                                      pointList[i + 1][0], pointList[i + 1][1],
                                      fill=CCOLOR)
            elementList.append(element)


def drawBezierCurve():
    """ draw bezier curve defined by (control-)points """

    parameter = []
    for i in range(n+1):
        t = a + (i/n)*(b-a)
        parameter.append(t)

    bezPoints = [pointList[0]]
    for i in range(n+1):
        bezPoints.append(casteljau(np.array(pointList), parameter[i]))
    bezPoints.append(pointList[-1])

    if len(bezPoints) > 1:
        for i in range(len(bezPoints) - 1):
            element = can.create_line(bezPoints[i][0], bezPoints[i][1],
                                      bezPoints[i + 1][0], bezPoints[i + 1][1],
                                      fill=BCOLOR)
            elementList.append(element)


def casteljau(points, t):

    if len(points) == 1:  # abbruch
        return points[0]

    newPoints = []
    for i in range(len(points)-1):
        p = (((b - t) / (b - a)) * points[i]) + (((t - a) / (b - a)) * points[i + 1])
        newPoints.append(p)

    return casteljau(newPoints, t)




def quit(root=None):
    """ quit programm """
    if root == None:
        sys.exit(0)
    root._root().quit()
    root._root().destroy()


def draw():
    """ draw elements """
    can.delete(*elementList)
    drawPoints()
    drawPolygon()
    drawBezierCurve()


def clearAll():
    """ clear all (point list and canvas) """
    can.delete(*elementList)
    del pointList[:]


def mouseEvent(event):
    """ process mouse events """
    print("left mouse button clicked at ", event.x, event.y)
    pointList.append([event.x, event.y])
    draw()


if __name__ == "__main__":
    # check parameters
    if len(sys.argv) != 1:
        print("pointViewerTemplate.py")
        sys.exit(-1)

    # create main window
    mw = Tk()

    # create and position canvas and buttons
    cFr = Frame(mw, width=WIDTH, height=HEIGHT, relief="sunken", bd=1)
    cFr.pack(side="top")
    can = Canvas(cFr, width=WIDTH, height=HEIGHT)
    can.bind("<Button-1>", mouseEvent)
    can.pack()
    cFr = Frame(mw)
    cFr.pack(side="left")
    bClear = Button(cFr, text="Clear", command=clearAll)
    bClear.pack(side="left")
    eFr = Frame(mw)
    eFr.pack(side="right")
    bExit = Button(eFr, text="Quit", command=(lambda root=mw: quit(root)))
    bExit.pack()

    # start
    mw.mainloop()
