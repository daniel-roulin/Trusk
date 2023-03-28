from renderer import Renderer
from linear_algebra import Vector3, Matrix4x4
from collections.abc import Iterable
import numpy as np
import matplotlib.colors as mc
import colorsys
import cProfile


#TODO: * operator overloading
class Triangle():
    def __init__(self, points: Iterable[Vector3] = [Vector3(), Vector3(), Vector3()]) -> None:
        self.p = np.array(points, dtype=Vector3)
        self.col = 0

    def __str__(self) -> str:
        return f"Triangle({self.p[0]}, {self.p[1]}, {self.p[2]})"

    def multiply_with_matrix(self, matrix: Matrix4x4):
        self.p[0].multiply_with_matrix(matrix)
        self.p[1].multiply_with_matrix(matrix)
        self.p[2].multiply_with_matrix(matrix)

    def __mul__(self, matrix):
        result = Triangle()
        result.col = self.col
        result.p[0] = self.p[0]*matrix
        result.p[1] = self.p[1]*matrix
        result.p[2] = self.p[2]*matrix
        return result


class Mesh():
    def __init__(self, triangles) -> None:
        self.triangles = np.array(triangles, dtype=Triangle)

    def load_from_file(path: str) -> None:
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
        return Mesh(triangles)


class Engine3D():
    def __init__(self) -> None:
        self.mesh = Mesh.load_from_file("cat.obj")
        self.mesh = Mesh.load_from_file("t_34_obj.obj")
        # self.mesh = Mesh(
        #     [
        #         Triangle([Vector3(), Vector3(0, 1, 0), Vector3(1, 1, 0)]),
        #         Triangle([Vector3(), Vector3(1, 1, 0), Vector3(1, 0, 0)]),
        #         Triangle([Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(1, 1, 1)]),
        #         Triangle([Vector3(1, 0, 0), Vector3(1, 1, 1), Vector3(1, 0, 1)]),
        #         Triangle([Vector3(1, 0, 1), Vector3(1, 1, 1), Vector3(0, 1, 1)]),
        #         Triangle([Vector3(1, 0, 1), Vector3(0, 1, 1), Vector3(0, 0, 1)]),
        #         Triangle([Vector3(0, 0, 1), Vector3(0, 1, 1), Vector3(0, 1, 0)]),
        #         Triangle([Vector3(0, 0, 1), Vector3(0, 1, 0), Vector3()]),
        #         Triangle([Vector3(0, 1, 0), Vector3(0, 1, 1), Vector3(1, 1, 1)]),
        #         Triangle([Vector3(0, 1, 0), Vector3(1, 1, 1), Vector3(1, 1, 0)]),
        #         Triangle([Vector3(1, 0, 1), Vector3(0, 0, 1), Vector3()]),
        #         Triangle([Vector3(1, 0, 1), Vector3(), Vector3(1, 0, 0)])
        #     ]
        # )

        self.vcamera = Vector3(3, 3, 2)
        self.vlookdir = Vector3(1, 0, 1)
        self.vlookdir.normalize()

        self.light_direction = Vector3(0, 1, 1)
        self.light_direction.normalize()

        # self.fyaw = 0

        # TODO: Fix aspect ratio
        self.mProj = Matrix4x4.projection(80, 1, 0.1, 1000)

    def update(self, r: Renderer, theta):
        # TODO: Add elapsed time
        # if r.is_key_pressed("up"):
        #     self.vcamera.y += 0.08
        # if r.is_key_pressed("down"):
        #     self.vcamera.y -= 0.08
        # if r.is_key_pressed("left"):
        #     self.vcamera.x += 0.08
        # if r.is_key_pressed("right"):
        #     self.vcamera.x -= 0.08

        # self.vforward = self.vlookdir*0.08

        # if r.is_key_pressed("w"):
        #     self.vcamera += self.vforward
        # if r.is_key_pressed("s"):
        #     self.vcamera -= self.vforward
        # if r.is_key_pressed("a"):
        #     self.fyaw -= 0.05
        # if r.is_key_pressed("d"):
        #     self.fyaw += 0.05

        # print(self.vcamera, self.fyaw)
        # print(np.random.randint(0, 10))

        # self.vcamera.z += 0.08

        # Skipped world transform here

        vup = Vector3(0, 1, 0)
        # vtarget = Vector3(0, 0, 1)
        # mcamera_rotation = Matrix4x4.rotationY(self.fyaw)
        # self.vlookdir = vtarget*mcamera_rotation

        self.vcamera = Vector3(np.cos(theta)*4, 2, np.sin(theta)*4)
        self.vlookdir = self.vcamera + Vector3(0, -3, 0)

        vtarget = self.vcamera + self.vlookdir
        self.mview = Matrix4x4.point_at(self.vcamera, vtarget, vup)
        self.mview.inverse()

        triangles_to_raster = []
        # TODO: fixed size array of viewed triangle, avoid calling np.array.
        for triangle in self.mesh.triangles:
            line1 = triangle.p[1] - triangle.p[0]
            line2 = triangle.p[2] - triangle.p[0]
            normal = Vector3.cross(line1, line2)
            normal.normalize()

            camera_ray = triangle.p[0] - self.vcamera
            if (Vector3.dot(normal, camera_ray) < 0.0):
                dp = Vector3.dot(self.light_direction, normal)

                triViewed = triangle*self.mview

                triViewed.col = self._adjust_lightness("#ffa75e", (dp+1)/2.5)

                triProjected = triViewed*self.mProj
                triProjected.p[0] /= triProjected.p[0].w
                triProjected.p[1] /= triProjected.p[1].w
                triProjected.p[2] /= triProjected.p[2].w

                triProjected.p[0].x *= -1
                triProjected.p[1].x *= -1
                triProjected.p[2].x *= -1
                triProjected.p[0].y *= -1
                triProjected.p[1].y *= -1
                triProjected.p[2].y *= -1

                vOffsetView = Vector3(1, 1, 0)
                triProjected.p[0] = triProjected.p[0] + vOffsetView
                triProjected.p[1] = triProjected.p[1] + vOffsetView
                triProjected.p[2] = triProjected.p[2] + vOffsetView
                triProjected.p[0].x *= r.WIDTH/2
                triProjected.p[0].y *= r.HEIGHT/2
                triProjected.p[1].x *= r.WIDTH/2
                triProjected.p[1].y *= r.HEIGHT/2
                triProjected.p[2].x *= r.WIDTH/2
                triProjected.p[2].y *= r.HEIGHT/2

                triangles_to_raster.append(triProjected)

        for t in triangles_to_raster:
            r.filled_triangle(t.p[0].x, t.p[0].y, t.p[1].x, t.p[1].y, t.p[2].x, t.p[2].y, color=t.col)

    def _line_plane_intersection(self, plane_p: Vector3, plane_n: Vector3, line_start: Vector3, line_end: Vector3) -> tuple[Vector3, float]:
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

    def _clip_against_plane(self, plane_p: Vector3, plane_n: Vector3, triangle: Triangle) -> tuple[int, Triangle | None, Triangle | None]:
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
            new_triangle.p[1] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])
            new_triangle.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[1])

            return 1, new_triangle, None

        if (n_inside_points == 2 and n_outside_points == 1):
            # Two points inside, we have a quad that we need to triangulate
            new_triangle1 = triangle
            new_triangle1.p[0] = inside_points[0]
            new_triangle1.p[1] = inside_points[1]
            new_triangle1.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])

            new_triangle2 = triangle
            new_triangle1.p[0] = inside_points[1]
            new_triangle1.p[1] = new_triangle1.p[2]
            new_triangle1.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[1], outside_points[0])

            return 2, new_triangle1, new_triangle2

    def _adjust_lightness(self, color, amount=0.5):
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], max(0, min(1, amount*c[1])), c[2])


def main():
    renderer = Renderer(width=200, height=200, target_fps=60)
    engine3d = Engine3D()

    theta = 0

    while True:
        engine3d.update(renderer, theta)
        renderer.draw()
        # exit()

        theta += 0.1


main()
