from renderer import Renderer
import math
import numpy as np

from functools import wraps
import time
def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        ts = np.empty(10)
        for i in range(10):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            ts[i] = total_time
            print(f'{i + 1}: Function {func.__name__} took {total_time:.4f} seconds')
        
        average = np.average(ts)
        print()
        print(f'Function {func.__name__} took on average {average:.4f} seconds')
        return result
    return timeit_wrapper


def adjust_lightness(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])
#region classes
class vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class triangle():
    def __init__(self, points):
        self.p = points
        self.sym = ""
        self.col = 0
        self.z = 0
        
class mesh():
    def __init__(self, triangles):
        self.triangles = triangles
        
class matrix4x4():
    def __init__(self):
        self.m = [[0, 0, 0, 0], 
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]
        
def get_object_from_file(filename):
    vertex, faces = [], []
    with open(filename) as f:
        for line in f:
            if line.startswith('v '):
                vertex_ = [float(i) for i in line.split()[1:]]
                vertex__ = vector3(vertex_[0], vertex_[1], vertex_[2])
                vertex.append(vertex__)
            elif line.startswith('f'):
                faces_ = line.split()[1:]
                faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
                
    triangles = []
    for tri in faces:
        triangle_ = triangle([vertex[tri[0]], vertex[tri[1]], vertex[tri[2]]])
        triangles.append(triangle_)
        if len(tri) > 3:
            triangle_ = triangle([vertex[tri[0]], vertex[tri[2]], vertex[tri[3]]])
            triangles.append(triangle_)
        
    return mesh(triangles)


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

meshCube = get_object_from_file('resources/t_34_obj.obj')
matProj = matrix4x4()

vCamera = vector3(0,0,0)

fTheta = 0

"""meshCube.triangles = [triangle([vector3(0, 0, 0), vector3(0, 1, 0), vector3(1, 1, 0)]),
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
"""
fNear = 0.1
fFar = 1000.0
fFov = 80
fAspectRatio = 1 #todo
fFovRad = 1.0 / math.tan(fFov * 0.5 / 180.0 * 3.14159)


matProj.m[0][0] = fAspectRatio * fFovRad
matProj.m[1][1] = fFovRad
matProj.m[2][2] = fFar / (fFar - fNear)
matProj.m[3][2] = (-fFar * fNear) / (fFar - fNear)
matProj.m[2][3] = 1.0
matProj.m[3][3] = 0.0

@timeit
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
    
    vecTrianglesToRaster = []
    
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
        triTranslated.p[0].z = triRotatedZX.p[0].z + -30.0
        triTranslated.p[1].z = triRotatedZX.p[1].z + -30.0
        triTranslated.p[2].z = triRotatedZX.p[2].z + -30.0

        normal = vector3(0,0,0)
        line1 = vector3(0,0,0)
        line2 = vector3(0,0,0)
        
        line1.x = triTranslated.p[1].x - triTranslated.p[0].x
        line1.y = triTranslated.p[1].y - triTranslated.p[0].y
        line1.z = triTranslated.p[1].z - triTranslated.p[0].z

        line2.x = triTranslated.p[2].x - triTranslated.p[0].x
        line2.y = triTranslated.p[2].y - triTranslated.p[0].y
        line2.z = triTranslated.p[2].z - triTranslated.p[0].z

        normal.x = line1.y * line2.z - line1.z * line2.y
        normal.y = line1.z * line2.x - line1.x * line2.z
        normal.z = line1.x * line2.y - line1.y * line2.x
        
        l = math.sqrt((normal.x*normal.x + normal.y*normal.y + normal.z*normal.z))
        normal.x /= l
        normal.y /= l
        normal.z /= l
        
        if(normal.x * (triTranslated.p[0].x - vCamera.x) + 
           normal.y * (triTranslated.p[0].y - vCamera.y) +
           normal.z * (triTranslated.p[0].z - vCamera.z) < 0.0):
            light_direction = vector3(0,0,-1)
            l = math.sqrt((light_direction.x*light_direction.x + light_direction.y*light_direction.y + light_direction.z*light_direction.z))
            light_direction.x /= l
            light_direction.y /= l
            light_direction.z /= l
            
            dp = normal.x * light_direction.x + normal.y * light_direction.y + normal.z * light_direction.z
            
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
            
            triProjected.col = dp
            vecTrianglesToRaster.append(triProjected)


        
        
    for t in vecTrianglesToRaster:
        r.filled_triangle(t.p[0].x, t.p[0].y, t.p[1].x, t.p[1].y, t.p[2].x, t.p[2].y, color = adjust_lightness("#ffa75e", (t.col+1)/2.5))


def main():
    r = Renderer(width=200, height=200, target_fps=60)
    angle = 1
    while True:
        angle += 0.05
        update(r, angle)
        r.draw()    
main()