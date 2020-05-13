from tkinter import *
#from Canvas import *
import sys, copy

WIDTH  = 400 # width of canvas
HEIGHT = 400 # height of canvas

HPSIZE = 2 # half of point size (must be integer)
CCOLOR = "#0000FF" # blue

elementList = [] # list of elements (used by Canvas.delete(...))

polygon = [[50,50],[350,50],[350,350],[50,350],[50,50]]
polygon_A = []
polygon_Z = []

time = 0
dt = 0.001

def drawObjekts():
    """ draw polygon and points """
    for (p,q) in zip(polygon,polygon[1:]):
        elementList.append(can.create_line(p[0], p[1], q[0], q[1],
                                           fill=CCOLOR))
        elementList.append(can.create_oval(p[0]-HPSIZE, p[1]-HPSIZE,
                                           p[0]+HPSIZE, p[1]+HPSIZE,
                                           fill=CCOLOR, outline=CCOLOR))
            


def quit(root=None):
    """ quit programm """
    if root==None:
        sys.exit(0)
    root._root().quit()
    root._root().destroy()


def draw():
    """ draw elements """
    can.delete(*elementList)
    del elementList[:]
    drawObjekts()
    can.update()


def forward():
    global time, polygon
    while(time<1):
        polygon.clear()
        time += dt
        for (p,q) in zip(polygon_A, polygon_Z):
            print((p,q))
            x = (1-time)*p[0] + time*q[0]
            y = (1-time)*p[1] + time*q[1]
            polygon.append([x, y])
        print(time)
        draw()


def backward():
    global time, polygon
    while(time>0):
        polygon.clear()
        time -= dt
        for (p,q) in zip(polygon_Z, polygon_A):
            x = (1-time)*q[0] + time*p[0]
            y = (1-time)*q[1] + time*p[1]
            polygon.append([x, y])
        print(time)
        draw()
    

if __name__ == "__main__":
    # check parameters
    if len(sys.argv) != 3:
       #print "morph.py firstPolygon secondPolygon"
       sys.exit(-1)

    print(sys.argv)

    # TODOS:
    # - read in polygons + transform from local into global coordinate system
    polygonA = open("polygonA.dat")
    for p in polygonA:
        print(p.split()[0])
        x = float(p.split()[0])*WIDTH
        y = (1 - float(p.split()[1]))*HEIGHT
        polygon_A.append((x,y))

    polygonZ = open("polygonZ.dat")
    for p in polygonZ:
        x = float(p.split()[0])*WIDTH
        y = (1 - float(p.split()[1]))*HEIGHT
        polygon_Z.append((x, y))

    # - make both polygons contain same number of points
    while len(polygon_A) > len(polygon_Z):
        polygon_Z.append(polygon_Z[0])

    while len(polygon_Z) > len(polygon_A):
        polygon_A.append(polygon_A[0])

    # copy A as starting point
    polygon = copy.deepcopy(polygon_A)

    # create main window
    mw = Tk()
    mw._root().wm_title("Morphing")

    # create and position canvas and buttons
    cFr = Frame(mw, width=WIDTH, height=HEIGHT, relief="sunken", bd=1)
    cFr.pack(side="top")
    can = Canvas(cFr, width=WIDTH, height=HEIGHT)
    can.pack()
    cFr = Frame(mw)
    cFr.pack(side="left")
    bClear = Button(cFr, text="backward", command=backward)
    bClear.pack(side="left")
    bClear = Button(cFr, text="forward", command=forward)
    bClear.pack(side="left")
    eFr = Frame(mw)
    eFr.pack(side="right")
    bExit = Button(eFr, text="Quit", command=(lambda root=mw: quit(root)))
    bExit.pack()
    draw()
    
    # start
    mw.mainloop()
    
