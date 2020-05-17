import math
from tkinter import *
import sys
import numpy as np

WIDTH = 400  # width of canvas
HEIGHT = 400  # height of canvas

HPSIZE = 1  # double of point size (must be integer)
COLOR = "#0000FF"  # blue

NOPOINTS = 1000

ALPHA = 10

pointList = []  # list of points (used by Canvas.delete(...))


def quit(root=None):
    """ quit programm """
    if root == None:
        sys.exit(0)
    root._root().quit()
    root._root().destroy()


def draw():
    """ draw points """
    can.delete('all')
    for p in transform(pointList):
        print(p)
        x,y = p
        can.create_oval(x - HPSIZE, y - HPSIZE, x + HPSIZE, y + HPSIZE,
                            fill=COLOR, outline=COLOR)


def rotYp():
    """ rotate counterclockwise around y axis """
    global pointList
    # NOPOINTS += 100
    pointList = rotateY(pointList, ALPHA)
    print("In rotYp: ", ALPHA)
    can.delete(*pointList)
    draw()


def rotYn():
    """ rotate clockwise around y axis """
    global pointList
    # NOPOINTS -= 100
    pointList = rotateY(pointList, -ALPHA)
    print("In rotYn: ", -ALPHA)
    can.delete(*pointList)
    draw()


def transform(pointList):

    max_coords = np.maximum.reduce([p for p in pointList])
    min_coords = np.minimum.reduce([p for p in pointList])

    moved_points = frustum(min_coords, max_coords, pointList)

    projected_points = parallelProject(moved_points)

    projected_points_xy = []

    for p in projected_points: # clip z coordinates
        p_xy = np.array([p[0],p[1],p[3]])
        projected_points_xy.append(p_xy)

    transformed_points = toViewPort(projected_points_xy)

    return transformed_points

def parallelProject(points):
    projected_points = []
    p_grundriss = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]])

    for p in points:
        p_point = np.dot(p_grundriss,p)
        projected_points.append(p_point)

    return projected_points

def toViewPort(points):
    transformed = []
    for p in points:
        p_x = (1+p[0]) * WIDTH/2.0
        p_y = (1-p[1]) * HEIGHT/2.0
        transformed.append(np.array([p_x, p_y]))

    return transformed

def frustum(min,max, points):
    xr = max[0]
    xl = min[0]
    yt = max[1]
    yb = min[1]
    zf = max[2]
    zn = min[2]

    t_ortho = np.array([
        [2.0/(xr-xl), 0,0,-(xr+xl)/(xr-xl)],
        [0, 2.0/(yt-yb), 0, -(yt+yb)/(yt-yb)],
        [0,0,-2/(zf-zn),-(zf+zn)/(zf-zn)],
        [0,0,0,1]
        ])

    moved_points = []
    for p in points:
        m_p = np.dot(t_ortho,p)
        moved_points.append(m_p)

    return moved_points

def rotateY(points, angle):
    sin = np.sin(math.radians(angle))
    cos = np.cos(math.radians(angle))

    m = np.array([[cos, 0, sin,0], [0, 1, 0,0], [-sin, 0, cos,0], [0,0,0,1]])
    print(m)
    points_rod = []

    for coords in points:
        rot_coords = np.dot(m, coords)
        points_rod.append(rot_coords)

    return points_rod


if __name__ == "__main__":
    # check parameters
    if len(sys.argv) != 2:
        print("pointViewerTemplate.py")
        sys.exit(-1)

    elif sys.argv[1].lower() in ("bunny", "elephant", "squirrel", "cow"):

        filename = f"{sys.argv[1]}_points.raw"
        f = open(filename).readlines()
        for coords in f:
            x, y, z = coords.split()
            point = np.array([float(x), float(y), float(z), 1.0])
            pointList.append(point)

    else:
        print("Invalid args received")
        sys.exit(-1)

    # create main window
    mw = Tk()

    # create and position canvas and buttons
    cFr = Frame(mw, width=WIDTH, height=HEIGHT, relief="sunken", bd=1)
    cFr.pack(side="top")
    can = Canvas(cFr, width=WIDTH, height=HEIGHT)
    can.pack()
    bFr = Frame(mw)
    bFr.pack(side="left")
    bRotYn = Button(bFr, text="<-", command=rotYn)
    bRotYn.pack(side="left")
    bRotYp = Button(bFr, text="->", command=rotYp)
    bRotYp.pack(side="left")
    eFr = Frame(mw)
    eFr.pack(side="right")
    bExit = Button(eFr, text="Quit", command=(lambda root=mw: quit(root)))
    bExit.pack()

    # draw points
    draw()

    # start
    mw.mainloop()
