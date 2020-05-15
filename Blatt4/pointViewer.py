from tkinter import *
import sys
import random
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

    moved_points = moveBox(min_coords,max_coords, pointList)

    scale = 2.0/ max(max_coords - min_coords)
    print(scale)

    scaled_points = [point * scale for point in moved_points]
    print(scaled_points)

    transformed_points = toViewPort(scaled_points)
    print(transformed_points)

    return transformed_points

def toViewPort(points):
    transformed = []
    for p in points:
        p_x = (1+p[0]) * WIDTH/2.0
        p_y = (1-p[1]) * HEIGHT/2.0
        transformed.append(np.array([p_x, p_y]))

    return transformed

def moveBox(min,max, points):
    print(min.item(0), max.item(0))
    center_x = (min.item(0) + max.item(0))/2
    center_y = (min.item(1) + max.item(1))/2
    center_z = (min.item(2) + max.item(2))/2

    center = np.array([center_x, center_y, center_z])
    print(center)

    moved_points = []
    for point in points:
        new_point = point - center
        moved_points.append(new_point)

    return moved_points

def rotateY(points, angle):
    sin = np.sin(angle)
    cos = np.cos(angle)

    m = np.array([[cos, 0, sin], [0, 1, 0], [-sin, 0, cos]])
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
            point = np.array([float(x), float(y), float(z)])
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
