import string
import time

from PIL import Image
import concurrent.futures

from Raytracing.Material import CheckerboardMaterial, Material
from Raytracing.Camera import Camera
from Raytracing.Color import Color
from Raytracing.Objects import *
from Raytracing.Ray import Ray
from Raytracing.generateMesh import TriForce, generateTriangles, rotateY

import sys


def intersect(ray, objectList, SQUIRREL):
    maxdist = float('inf')
    object = None
    point = None
    # matrices = rotateY(180)
    for obj in objectList:
        hitdist = obj.intersectionParameter(ray)
        if hitdist:
            if 0.0001 < hitdist < maxdist: # account for rounding errors
                maxdist = hitdist
                object = obj
                # ray.direction = np.dot(ray.direction, matrices[1])
                point = ray.pointAtParameter(maxdist - .1)
                # point = np.dot(point, matrices[0])
    if object is None:
        return None
    else:
        return object, point, ray


def traceRay(level, ray, objectList, lightsources, MAXLEVEL, SQUIRREL):
    hitPointData = intersect(ray, objectList, SQUIRREL)
    if hitPointData:
        return shade(level, hitPointData, objectList, lightsources, MAXLEVEL, SQUIRREL)
    return Color(0, 0, 0) # else return black


def shade(level, hitPointData, objectList, lightsources, MAXLEVEL, SQUIRREL):
    obj, point, ray = hitPointData
    if not SQUIRREL:
        reflection = obj.material.reflectionFactor  # ~specularCoefficient except plane so it doesnt reflect back, deactivated for squirrel
    else:
        reflection = 0

    directColor = computeDirectLight(hitPointData, objectList, lightsources, SQUIRREL)

    if level == MAXLEVEL:
        return directColor

    reflectedRay = computeReflectedRay(hitPointData)
    reflectColor = traceRay(level + 1, reflectedRay, objectList, lightsources, MAXLEVEL, SQUIRREL)

    return directColor + reflection * reflectColor


def inShadow(lightray, obj, objectList):
    for object in objectList:
        if object is not obj:
            intersection = object.intersectionParameter(lightray)
            if intersection > 0.0001:
                return True
    return False


def computeDirectLight(hitPointData, objectList, lightsources, SQUIRREL):
    obj, point, ray = hitPointData
    lightray = Ray(lightsources[0], point - lightsources[0]) # vector from lightsource to intersection point
    normal = obj.normalAt(point)

    if not SQUIRREL: # deactivate shadows for squirrel to save time
        if inShadow(lightray, obj, objectList):
            return 0.4 * obj.material.ambientCoefficient * obj.material.baseColorAt(point) # using 0.4 as shadow intensity
        else:
            return obj.material.calcColor(lightray, normal, ray, point)
    else:
        return obj.material.calcColor(lightray, normal, ray, point)


def computeReflectedRay(hitPointData):
    obj, point, ray = hitPointData
    normal = obj.normalAt(point)
    direction_in = ray.direction
    direction_out = direction_in - (
            2 * normal * (np.dot(normal, direction_in)))  # Einfallswinkel = Ausfallswinkel
    return Ray(point, direction_out)


def render(image, objectList, level=0):
    for x in range(camera.wRes):
        for y in range(camera.hRes):
            print(x, y)
            ray = camera.calcRay(x, y)
            color = tuple(traceRay(level, ray, objectList, lightsources, MAXLEVEL, SQUIRREL).getColor())
            image.putpixel((x, y), color)


def multiRender(camera, objList, lightsources, MAXLEVEL, SQUIRREL, subspace, level=0):
    img_data = []
    for x in range(subspace[0], subspace[1]):
        for y in range(subspace[2], subspace[3]):
            print(x, y)
            ray = camera.calcRay(x, y)
            color = tuple(traceRay(level, ray, objList, lightsources, MAXLEVEL, SQUIRREL).getColor())
            img_data.append((x, y, color))
    return img_data


def main(image, data):
    print("Starting...")
    if MULTIPROCESSING:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            p1 = executor.submit(multiRender, *(camera, objectList, lightsources, MAXLEVEL, SQUIRREL, data[0]))
            p2 = executor.submit(multiRender, *(camera, objectList, lightsources, MAXLEVEL, SQUIRREL, data[1]))
            p3 = executor.submit(multiRender, *(camera, objectList, lightsources, MAXLEVEL, SQUIRREL, data[2]))
            p4 = executor.submit(multiRender, *(camera, objectList, lightsources, MAXLEVEL, SQUIRREL, data[3]))

            parts = [p1, p2, p3, p4]
            for part in parts:
                for x, y, color in part.result():
                    image.putpixel((x, y), color)
    else:
        render(image, objectList)


if __name__ == '__main__':

    # Mode
    TEXTURE = False
    SQUIRREL = False

    # Processing
    MULTIPROCESSING = True

    if len(sys.argv) < 2:
        print("NO ARGUMENTS GIVEN! RENDERING PICTURE 1 WITH MULTIPROCESSING")
        time.sleep(2.0)

    if len(sys.argv) > 1:

        if sys.argv[1] == '1':
            TEXTURE = False
            print("RENDERING PICTURE 1 - NO TEXTURE")

        elif sys.argv[1] == '2':
            TEXTURE = True
            print("RENDERING PICTURE 2 - W/ TEXTURE")

        elif sys.argv[1] == '3':
            SQUIRREL = True
            print("RENDERING PICTURE 3 - SQUIRREL")

        elif sys.argv[1] not in (1, 2, 3):
            TEXTURE = False
            SQUIRREL = False
            print("INVALID ARGUMENT GIVEN! RENDERING PICTURE 1!")

        time.sleep(1.0)

    if len(sys.argv) > 2:

        if str(sys.argv[2]).lower() == "off":
            MULTIPROCESSING = False
            print("RENDERING PICTURE W/O MULTIPROCESSING :( ")

        elif str(sys.argv[2]).lower() == "on":
            MULTIPROCESSING = True
            print("RENDERING PICTURE WITH MULTIPROCESSING :) ")

        else:
            print("INVALID ARGUMENT GIVEN! RENDERING PICTURE WITH MULTIPROCESSING")

        time.sleep(1.0)

    if len(sys.argv) > 3:
        print("MAXIMUM ARGUMENTS EXCEEDED! IGNORING REST")
        time.sleep(1.0)

    # Size
    WIDTH = 100
    HEIGHT = 100

    # Lightsources
    L1 = np.array([30, 30, 10])
    L2 = np.array([-30, 100, 10])

    lightsources = []
    if TEXTURE:
        lightsources = [L2]
    else:
        lightsources = [L1]

    # Camera
    e = np.array([0, 1.8, 10])
    c = np.array([0, 3, 0])
    up = np.array([0, 1, 0])
    FOV = 45

    # So the squirrel faces forward
    e2 = np.array([0, 2, -10])
    c2 = np.array([0, 0, 0])

    if not SQUIRREL:
        camera = Camera(e, c, up, FOV, WIDTH, HEIGHT)
    else:
        camera = Camera(e2, c2, up, FOV, WIDTH, HEIGHT)

    # Colors
    BASECOLOR = Color(255, 255, 255)  # white
    OTHERCOLOR = Color(0, 0, 0)  # black
    BLUE = Color(0, 0, 255)
    GREEN = Color(0, 255, 0)
    RED = Color(255, 0, 0)
    YELLOW = Color(255, 255, 0)
    GREY = Color(105, 105, 105)

    # Shapes & Materials
    materials = {
        'checkerboard': CheckerboardMaterial(),
        'blue': Material(BLUE),
        'green': Material(GREEN),
        'red': Material(RED),
        'yellow': Material(YELLOW),
        'grey': Material(GREY, 1, 0),
        'white': Material(BASECOLOR)
    }

    if TEXTURE:
        objectList = [Sphere(np.array([2.5, 3, -10]), 2, materials['red']),
                      Sphere(np.array([-2.5, 3, -10]), 2, materials['green']),
                      Sphere(np.array([0, 7, -10]), 2, materials['blue']),
                      Triangle(np.array([2.5, 3, -10]), np.array([-2.5, 3, -10]), np.array([0, 7, -10]),
                               materials['yellow']),
                      Plane(np.array([0, 0, 0]), np.array([0, 1, 0]), materials['checkerboard'])]

    elif SQUIRREL:
        triangles = generateTriangles(TriForce('squirrel_aligned_lowres.obj'))
        objectList = [Plane(np.array([0, 0, 0]), np.array([0, 1, 0]), materials['checkerboard'])]
        for triangle in triangles:
            objectList.append(Triangle(triangle[0], triangle[1], triangle[2], materials['grey']))
    else:
        objectList = [Sphere(np.array([2.5, 3, -10]), 2, materials['red']),
                      Sphere(np.array([-2.5, 3, -10]), 2, materials['green']),
                      Sphere(np.array([0, 7, -10]), 2, materials['blue']),
                      Triangle(np.array([2.5, 3, -10]), np.array([-2.5, 3, -10]), np.array([0, 7, -10]),
                               materials['yellow']), Plane(np.array([0, 0, 0]), np.array([0, 1, 0]), materials['grey'])]

    if not SQUIRREL:
        MAXLEVEL = 5  # Rekursionstiefe
    else:
        MAXLEVEL = 1

    # image split into 4 equal parts. Mabye it won't work if width != height
    subspaces = [
        [0, camera.wRes // 2, 0, camera.hRes // 2],
        [camera.wRes // 2, camera.wRes, 0, camera.hRes // 2],
        [0, camera.wRes // 2, camera.hRes // 2, camera.hRes],
        [camera.wRes // 2, camera.wRes, camera.hRes // 2, camera.hRes]
    ]

    scene = Image.new('RGB', (WIDTH, HEIGHT))
    start = time.time()
    print(str(start))
    main(scene, subspaces)
    print("Ending...")
    print("Rendering took %s seconds" % (time.time() - start))
    scene.show()
    # scene.save('scene.png', 'PNG')
