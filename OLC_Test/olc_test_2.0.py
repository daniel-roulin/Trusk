from renderer import Renderer
import math
import numpy as np

#region classes
class vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class triangle():
    def __init__(self, points):
        self.p = points
        
class mesh():
    def __init__(self, triangles):
        self.triangles = triangles
        
class matrix4x4():
    def __init__(self):
        self.m = [[0, 0, 0, 0], 
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]

def multiplyMatrixVector(i, m):
    result = vector3(0,0,0)
    result.x = i.x * m.m[0][0] + i.y * m.m[1][0] + i.z * m.m[2][0] + m.m[3][0]
    result.y = i.x * m.m[0][1] + i.y * m.m[1][1] + i.z * m.m[2][1] + m.m[3][1];
    result.z = i.x * m.m[0][2] + i.y * m.m[1][2] + i.z * m.m[2][2] + m.m[3][2];
    
    w = i.x * m.m[0][3] + i.y * m.m[1][3] + i.z * m.m[2][3] + m.m[3][3];
    
    if (w != 0.0):
        result.x /= w
        result.y /= w
        result.z /= w
        
    return result

meshCube = mesh(None)
matProj = matrix4x4()
fTheta = 0

meshCube.triangles = [triangle([vector3(0, 0, 0), vector3(0, 1, 0), vector3(1, 1, 0)]),
                      triangle([vector3(0, 0, 0), vector3(1, 1, 0), vector3(1, 0, 0)]),
                      
                      triangle([vector3(1, 0, 0), vector3(1, 1, 0), vector3(1, 1, 1)]),
                      triangle([vector3(1, 0, 0), vector3(1, 1, 1), vector3(1, 0, 1)]),
                      
                      triangle([vector3(1, 0, 1), vector3(1, 1, 1), vector3(0, 1, 1)]),
                      triangle([vector3(1, 0, 1), vector3(0, 1, 1), vector3(0, 0, 1)]),
                      
                      triangle([vector3(0, 0, 1), vector3(0, 1, 1), vector3(0, 1, 0)]),
                      triangle([vector3(0, 0, 1), vector3(0, 1, 0), vector3(0, 0, 0)]),
                      
                      triangle([vector3(0, 1, 0), vector3(0, 1, 1), vector3(1, 1, 1)]),
                      triangle([vector3(0, 1, 0), vector3(1, 1, 1), vector3(1, 1, 0)]),
                      
                      triangle([vector3(1, 0, 1), vector3(0, 0, 1), vector3(0, 0, 0)]),
                      triangle([vector3(1, 0, 1), vector3(0, 0, 0), vector3(1, 0, 0)])]

fNear = 0.1
fFar = 1000.0
fFov = 90.0
fAspectRatio = 1 #todo
fFovRad = 1.0 / math.tan(fFov * 0.5 / 180.0 * 3.14159)
print(matProj.m)

matProj.m[0][0] = fAspectRatio * fFovRad
matProj.m[1][1] = fFovRad
matProj.m[2][2] = fFar / (fFar - fNear)
matProj.m[3][2] = (-fFar * fNear) / (fFar - fNear)
matProj.m[2][3] = 1.0
matProj.m[3][3] = 0.0

def update(r, fTheta):
    matRotZ = matrix4x4()
    matRotX = matrix4x4()

    matRotZ.m[0][0] = math.cos(fTheta)
    matRotZ.m[0][1] = math.sin(fTheta)
    matRotZ.m[1][0] = -math.sin(fTheta)
    matRotZ.m[1][1] = math.cos(fTheta)
    matRotZ.m[2][2] = 1
    matRotZ.m[3][3] = 1

    matRotX.m[0][0] = 1
    matRotX.m[1][1] = math.cos(fTheta * 0.5)
    matRotX.m[1][2] = math.sin(fTheta * 0.5)
    matRotX.m[2][1] = -math.sin(fTheta * 0.5)
    matRotX.m[2][2] = math.cos(fTheta * 0.5)
    matRotX.m[3][3] = 1
    
    for tri in meshCube.triangles:
    
        triProjected = triangle([vector3(0, 0, 0), vector3(0, 0, 0), vector3(0, 0, 0)])
        triTranslated = triangle([vector3(0, 0, 0), vector3(0, 0, 0), vector3(0, 0, 0)])
        triRotatedZ = triangle([vector3(0, 0, 0), vector3(0, 0, 0), vector3(0, 0, 0)])
        triRotatedZX = triangle([vector3(0, 0, 0), vector3(0, 0, 0), vector3(0, 0, 0)])

        triRotatedZ.p[0] = multiplyMatrixVector(tri.p[0], matRotZ)
        triRotatedZ.p[1] = multiplyMatrixVector(tri.p[1], matRotZ)
        triRotatedZ.p[2] = multiplyMatrixVector(tri.p[2], matRotZ)

        triRotatedZX.p[0] = multiplyMatrixVector(triRotatedZ.p[0], matRotX)
        triRotatedZX.p[1] = multiplyMatrixVector(triRotatedZ.p[1], matRotX)
        triRotatedZX.p[2] = multiplyMatrixVector(triRotatedZ.p[2], matRotX)


        triTranslated = triRotatedZX
        triTranslated.p[0].z = triRotatedZX.p[0].z + 3.0
        triTranslated.p[1].z = triRotatedZX.p[1].z + 3.0
        triTranslated.p[2].z = triRotatedZX.p[2].z + 3.0

        triProjected.p[0] = multiplyMatrixVector(triTranslated.p[0], matProj)
        triProjected.p[1] = multiplyMatrixVector(triTranslated.p[1], matProj)
        triProjected.p[2] = multiplyMatrixVector(triTranslated.p[2], matProj)


        triProjected.p[0].x += 1.0
        triProjected.p[0].y += 1.0
        triProjected.p[1].x += 1.0
        triProjected.p[1].y += 1.0
        triProjected.p[2].x += 1.0
        triProjected.p[2].y += 1.0
        
        triProjected.p[0].x *= 0.5 * 200
        triProjected.p[0].y *= 0.5 * 200
        triProjected.p[1].x *= 0.5 * 200
        triProjected.p[1].y *= 0.5 * 200
        triProjected.p[2].x *= 0.5 * 200
        triProjected.p[2].y *= 0.5 * 200

        r.filled_triangle(triProjected.p[0].x, triProjected.p[0].y, triProjected.p[1].x, triProjected.p[1].y, triProjected.p[2].x, triProjected.p[2].y, color = "#eb8f44")

def main():
    r = Renderer(width=200, height=200, target_fps=60)
    angle = 1
    while True:
        angle += 0.01
        update(r, angle)
        r.draw()    
main()