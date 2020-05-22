import math
from tkinter import *
import sys
import numpy as np

WIDTH = 400  # width of canvas
HEIGHT = 400  # height of canvas

HPSIZE = 1  # double of point size (must be integer)
COLOR = "#0000FF"  # blue

NOPOINTS = 1000

ALPHA = 30
ASPECT = WIDTH/HEIGHT
near = 1
far = 3

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

    center = (max_coords - min_coords) / 2.0 + min_coords
    radius = np.linalg.norm(center-min_coords)

    looked_points = lookAt(radius, pointList)
    projected_points = perspectivelProject(looked_points)
    projected_points_xy = []

    for p in projected_points: # clip z coordinates
        p_xy = np.array([p[0],p[1],p[3]])
        projected_points_xy.append(p_xy)

    transformed_points = toViewPort(projected_points_xy)

    return transformed_points

def lookAt(r, points):
    camera_points = []
    e = np.array([0,0,2*r])
    c = np.array([0,0,0])
    up = np.array([0,1,0])
    up_norm = up/np.linalg.norm(up)

    f = (c - e) / np.linalg.norm(c - e)
    s = np.cross(f, up_norm) / np.linalg.norm(np.cross(f, up_norm))
    u = np.cross(s, f)

    m_la = np.array([
        [s[0],s[1],s[2],-np.dot(s,e)],
        [u[0],u[1],u[2],-np.dot(u,e)],
        [-f[0],-f[1],-f[2],np.dot(f,e)],
        [0,0,0,1]
    ])

    for p in points:
        p_la = np.dot(m_la, p)
        camera_points.append(p_la)

    return camera_points

def perspectivelProject(points):
    projected_points = []
    cot = np.cos(math.radians(ALPHA))/np.sin(math.radians(ALPHA))

    t_pers = np.array([
        [cot/ASPECT, 0,0,0],
        [0,cot,0,0],
        [0, 0, -(far + near) / (far - near), (-2 * far * near) / (far - near)],
        [0,0,-1,0]
    ])

    for p in points:
        m_p = np.dot(t_pers,p)
        m_p_div = np.array([m_p[0] / m_p[3], m_p[1] / m_p[3], m_p[2] / m_p[3], m_p[3] / m_p[3]])  # prespective division
        projected_points.append(m_p_div)

    return projected_points

def toViewPort(points):
    transformed = []
    for p in points:
        p_x = (1+p[0]) * WIDTH/2.0
        p_y = (1-p[1]) * HEIGHT/2.0
        transformed.append(np.array([p_x, p_y]))

    return transformed

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