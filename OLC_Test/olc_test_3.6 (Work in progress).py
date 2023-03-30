from renderer import Renderer
from linear_algebra import Vector3, Matrix4x4
from collections.abc import Iterable
import numpy as np
import matplotlib.colors as mc
import colorsys
import cProfile

#TODO: default value 0,0,0 for Vector3


#region classes
#TODO: * operator overloading
class Triangle():
    def __init__(self, points: Iterable[Vector3] = [Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(0, 0, 0)]) -> None:
        self.p = np.array(points, dtype=Vector3)
        self.col = 0

    def __str__(self) -> str:
        return f"Triangle({self.p[0]}, {self.p[1]}, {self.p[2]})"


class Mesh():
    def __init__(self) -> None:
        self.triangles = []

    def load_from_file(self, path: str) -> None:
        vertices, faces = [], []
        with open(path) as f:
            for line in f:
                if line.startswith('v '):
                    vector = Vector3(*[float(v) for v in line.split()[1:]])
                    vertices.append(vector)
                elif line.startswith('f'):
                    face = line.split()[1:]
                    faces.append([int(f.split('/')[0]) - 1 for f in face])

        triangles = []
        for tri in faces:
            triangle = Triangle([vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]])
            triangles.append(triangle)
            if len(tri) > 3:
                triangle = Triangle([vertices[tri[0]], vertices[tri[2]], vertices[tri[3]]])
                triangles.append(triangle)
        self.triangles = np.array(triangles, dtype=Triangle)


#endregion


#region functions
def line_plane_intersection(plane_p: Vector3, plane_n: Vector3, line_start: Vector3, line_end: Vector3) -> tuple[Vector3, float]:
    """
    Returns the point of intersection between a plane and a line.
    """
    plane_n.normalize()
    plane_d = -Vector3.dot(plane_n, plane_p)
    ad = Vector3.dot(line_start, plane_n)
    bd = Vector3.dot(line_end, plane_n)
    t = (-plane_d - ad)/(bd-ad)
    line_vec = line_end - line_start
    line_to_intersect = line_vec*t
    return line_start + line_to_intersect


def clip_against_plane(plane_p: Vector3, plane_n: Vector3, triangle: Triangle) -> tuple[int, Triangle | None, Triangle | None]:
    """
    Clip the triangle against the plane and returns the number of valid triangles inside.
    Also returns one or two triangles that are guaranteed to be inside.
    """
    plane_n.normalize()

    inside_points = np.empty(3, dtype=Vector3)
    outside_points = np.empty(3, dtype=Vector3)
    n_inside_points = 0
    n_outside_points = 0

    d0 = triangle.p[0].distance_to_plane(plane_p, plane_n)
    d1 = triangle.p[1].distance_to_plane(plane_p, plane_n)
    d2 = triangle.p[2].distance_to_plane(plane_p, plane_n)

    if (d0 >= 0):
        inside_points[n_inside_points] = triangle.p[0]
        n_inside_points += 1
    else:
        outside_points[n_outside_points] = triangle.p[0]
        n_inside_points += 1
    if (d1 >= 0):
        inside_points[n_inside_points] = triangle.p[1]
        n_inside_points += 1
    else:
        outside_points[n_outside_points] = triangle.p[1]
        n_inside_points += 1
    if (d2 >= 0):
        inside_points[n_inside_points] = triangle.p[2]
        n_inside_points += 1
    else:
        outside_points[n_outside_points] = triangle.p[2]
        n_inside_points += 1

    if (n_inside_points == 0):
        # Completely clipped
        return 0, None, None

    if n_inside_points == 3:
        # Not clipped at all
        return 1, triangle, None

    if (n_inside_points == 1 and n_outside_points == 2):
        # Two points on the outside => We just make the triangle smaller
        new_triangle = triangle
        new_triangle.p[0] = inside_points[0]
        new_triangle.p[1] = line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])
        new_triangle.p[2] = line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[1])

        return 1, new_triangle, None

    if (n_inside_points == 2 and n_outside_points == 1):
        # Two points inside, we have a quad that we need to triangulate
        new_triangle1 = triangle
        new_triangle1.p[0] = inside_points[0]
        new_triangle1.p[1] = inside_points[1]
        new_triangle1.p[2] = line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])

        new_triangle2 = triangle
        new_triangle1.p[0] = inside_points[1]
        new_triangle1.p[1] = new_triangle1.p[2]
        new_triangle1.p[2] = line_plane_intersection(plane_p, plane_n, inside_points[1], outside_points[0])

        return 2, new_triangle1, new_triangle2


def adjust_lightness(color, amount=0.5):
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount*c[1])), c[2])


#endregion

mesh = Mesh()
# mesh.load_from_file("resources/t_34_obj.obj")
mesh.triangles = [
    Triangle([Vector3(0, 0, 0), Vector3(0, 1, 0), Vector3(1, 1, 0)]),
    Triangle([Vector3(0, 0, 0), Vector3(1, 1, 0), Vector3(1, 0, 0)]),
    Triangle([Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(1, 1, 1)]),
    Triangle([Vector3(1, 0, 0), Vector3(1, 1, 1), Vector3(1, 0, 1)]),
    Triangle([Vector3(1, 0, 1), Vector3(1, 1, 1), Vector3(0, 1, 1)]),
    Triangle([Vector3(1, 0, 1), Vector3(0, 1, 1), Vector3(0, 0, 1)]),
    Triangle([Vector3(0, 0, 1), Vector3(0, 1, 1), Vector3(0, 1, 0)]),
    Triangle([Vector3(0, 0, 1), Vector3(0, 1, 0), Vector3(0, 0, 0)]),
    Triangle([Vector3(0, 1, 0), Vector3(0, 1, 1), Vector3(1, 1, 1)]),
    Triangle([Vector3(0, 1, 0), Vector3(1, 1, 1), Vector3(1, 1, 0)]),
    Triangle([Vector3(1, 0, 1), Vector3(0, 0, 1), Vector3(0, 0, 0)]),
    Triangle([Vector3(1, 0, 1), Vector3(0, 0, 0), Vector3(1, 0, 0)])
]

vCamera = Vector3(0, 0, 0)

fTheta = 0

# TODO: Fix aspect ratio
matProj = Matrix4x4.projection(80, 1, 0.1, 1000)


# @timing
def update(r, theta):
    matRotZ = Matrix4x4.rotationZ(theta)

    matRotX = Matrix4x4.rotationX(theta/2)

    vecTrianglesToRaster = []
    for triangle in mesh.triangles:
        triRotatedZ = Triangle()
        for i in range(3):
            triRotatedZ.p[i] = triangle.p[i]*matRotZ

        triRotatedZX = Triangle()
        for i in range(3):
            triRotatedZX.p[i] = triRotatedZ.p[i]*matRotX

        triTranslated = Triangle()
        triTranslated = triRotatedZX
        for i in range(3):
            triTranslated.p[i] += Vector3(0, 0, -30, 0)

        line1 = triTranslated.p[1] - triTranslated.p[0]
        line2 = triTranslated.p[2] - triTranslated.p[0]

        normal = Vector3.cross(line1, line2)
        normal.normalize()

        camera_ray = triTranslated.p[0] - vCamera
        if (Vector3.dot(normal, camera_ray) < 0.0):
            #FIXME: This is broken
            # TODO: light direction calc does not need to be in loop
            light_direction = Vector3(0, 0, -1)
            light_direction.normalize()
            dp = Vector3.dot(light_direction, normal)

            triProjected = Triangle()
            for i in range(3):
                triProjected.p[i] = triTranslated.p[i]*matProj
                triProjected.p[i] /= triProjected.p[i].w

            triProjected.p[0].x += 1.0
            triProjected.p[0].y += 1.0
            triProjected.p[1].x += 1.0
            triProjected.p[1].y += 1.0
            triProjected.p[2].x += 1.0
            triProjected.p[2].y += 1.0

            triProjected.p[0].x *= 0.5*200
            triProjected.p[0].y *= 0.5*200
            triProjected.p[1].x *= 0.5*200
            triProjected.p[1].y *= 0.5*200
            triProjected.p[2].x *= 0.5*200
            triProjected.p[2].y *= 0.5*200

            triProjected.col = dp
            vecTrianglesToRaster.append(triProjected)

    for t in vecTrianglesToRaster:
        r.filled_triangle(t.p[0].x, t.p[0].y, t.p[1].x, t.p[1].y, t.p[2].x, t.p[2].y, color=adjust_lightness("#ffa75e", (t.col + 1)/2.5))


def main():
    r = Renderer(width=200, height=200, target_fps=60)
    angle = 1
    while True:
        angle += 0.05
        update(r, angle)
        r.draw()
        # exit()


main()
# cProfile.run("main()", sort="time")
