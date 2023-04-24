from renderer import Renderer
import numpy as np
import matplotlib.colors as mc
import colorsys
import cProfile
from matrix import Matrix4x4, Matrix3x3
import keyboard

from functools import wraps
import time


def scale(val, src_start, src_stop, dst_start, dst_stop):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val-src_start)/(src_stop-src_start))*(dst_stop-dst_start) + dst_start


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


class Mesh():
    def __init__(self, triangles) -> None:
        # TODO: Can probably improve performances by using less precision/fixed point in dtype
        self.triangles = np.array(triangles, dtype=float)

    def load_from_file(path: str) -> None:
        vertices, faces = [], []
        with open(path) as f:
            for line in f:
                if line.startswith('v '):
                    vector = [float(v) for v in line.split()[1:]]
                    vector.append(1)
                    vertices.append(vector)
                elif line.startswith('f'):
                    face = line.split()[1:]
                    faces.append([int(f.split('/')[0]) - 1 for f in face])

        triangles = []
        for tri in faces:
            triangle = [vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]]
            triangles.append(triangle)
            if len(tri) > 3:
                triangle = [vertices[tri[0]], vertices[tri[2]], vertices[tri[3]]]
                triangles.append(triangle)
        return Mesh(triangles)


class Engine3D():
    def __init__(self, aspect_ratio) -> None:
        # self.mesh = Mesh.load_from_file("t_34_obj.obj")
        self.mesh = Mesh.load_from_file("cat.obj")
        # self.mesh = Mesh(
        #     [
        #         [[0, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]],
        #         [[0, 0, 0, 1], [1, 1, 0, 1], [1, 0, 0, 1]],
        #         [[1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1]],
        #         [[1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1]],
        #         [[1, 0, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]],
        #         [[1, 0, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1]],
        #         [[0, 0, 1, 1], [0, 1, 1, 1], [0, 1, 0, 1]],
        #         [[0, 0, 1, 1], [0, 1, 0, 1], [0, 0, 0, 1]],
        #         [[0, 1, 0, 1], [0, 1, 1, 1], [1, 1, 1, 1]],
        #         [[0, 1, 0, 1], [1, 1, 1, 1], [1, 1, 0, 1]],
        #         [[1, 0, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]],
        #         [[1, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]],
        #     ]
        # )

        # Cat referential: [left/right, up/down, front/back]
        self.camera_position = np.array([0, 2, 5], dtype=float)

        self.look_direction = np.array([0, 0, 1], dtype=float)
        self.look_direction /= np.linalg.norm(self.look_direction)

        self.light_direction = np.array([0, 0, 1], dtype=float)
        self.light_direction /= np.linalg.norm(self.light_direction)

        self.projection_matrix = Matrix4x4.projection(80, aspect_ratio, 0.1, 1000)
        self.yaw = 0

        self.forward = self.look_direction*0.08

        self.right = np.zeros(3)
        self.right[0] = self.forward[1]
        self.right[1] = -self.forward[0]

    # @timeit
    def update(self, r: Renderer):
        self.forward = self.look_direction*0.08
        self.right[0] = self.forward[2]
        self.right[2] = -self.forward[0]
        if keyboard.is_pressed("w"):
            self.camera_position -= self.forward
        if keyboard.is_pressed("s"):
            self.camera_position += self.forward
        if keyboard.is_pressed("a"):
            self.camera_position -= self.right
        if keyboard.is_pressed("d"):
            self.camera_position += self.right
        if keyboard.is_pressed("space"):
            self.camera_position[1] += 0.08
        if keyboard.is_pressed("shift"):
            self.camera_position[1] -= 0.08

        up = np.array([0, 1, 0], dtype=float)
        target = np.array([0, 0, 1], dtype=float)

        # A movement on the x axis is a rotation on the y axis and vice versa
        rot_x = scale(r.mouse_y, 0, r.WIDTH, 0, np.pi)
        rot_y = scale(r.mouse_x, 0, r.HEIGHT, 0, np.pi)

        camera_rotation_x = Matrix3x3.rotationX(rot_x)
        camera_rotation_y = Matrix3x3.rotationY(rot_y)

        camera_rotation = camera_rotation_x @ camera_rotation_y
        self.look_direction = target @ camera_rotation

        target = self.camera_position + self.look_direction
        self.camera_matrix = Matrix4x4.point_at(self.camera_position, target, up)
        self.view_matrix = np.linalg.inv(self.camera_matrix)

        triangles = self.mesh.triangles

        # TODO: Precompute normals
        line1 = triangles[:, 1, :3] - triangles[:, 0, :3]
        line2 = triangles[:, 2, :3] - triangles[:, 0, :3]
        normals = np.cross(line1, line2)
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]

        # Calculate dot product of normal and camera ray for all triangles
        camera_rays = triangles[:, 0, :3] - self.camera_position

        # Dark stackoverflow magic to simply perform a dot product
        # (Source: https://stackoverflow.com/questions/63301019/dot-product-of-two-numpy-arrays-with-3d-vectors)
        visibility_dot_products = np.einsum('ij,ij->i', normals, camera_rays)

        # Filter out triangles that are not visible
        visible_triangles = triangles[visibility_dot_products < 0]

        # Rasterize visible triangles
        # We move the triangles in front of the camera
        viewed_triangles = visible_triangles @ self.view_matrix

        # Alignment of the traingle's normals with the light
        light_dot_product = np.dot(self.light_direction, normals[visibility_dot_products < 0].T)

        # Can be greatly optimized by adjusting lightness manually
        colors = np.empty((viewed_triangles.shape[0], 3))
        for i in range(viewed_triangles.shape[0]):
            colors[i] = np.array(self._adjust_lightness("#ffa75e", (light_dot_product[i] + 1)/2.5))

        # We project the triangles: we "squish" them triangles onto the screen
        projected_triangles = viewed_triangles @ self.projection_matrix
        projected_triangles[:, 0] /= projected_triangles[:, 0][:, np.newaxis, -1]
        projected_triangles[:, 1] /= projected_triangles[:, 1][:, np.newaxis, -1]
        projected_triangles[:, 2] /= projected_triangles[:, 2][:, np.newaxis, -1]
        projected_triangles[:, :, :2] *= np.array([-1, -1])[np.newaxis, :]
        projected_triangles[:, :, :2] *= np.array([r.WIDTH/2, r.HEIGHT/2])[np.newaxis, :]

        for i in range(projected_triangles.shape[0]):
            t = projected_triangles[i]
            r.filled_triangle(t[0, 0], t[0, 1], t[1, 0], t[1, 1], t[2, 0], t[2, 1], color=colors[i])

    def _line_plane_intersection(self, plane_p, plane_n, line_start, line_end):
        """
        Returns the point of intersection between a plane and a line.
        """
        # plane_n.normalize()
        # plane_d = -Vector3.dot(plane_n, plane_p)
        # ad = Vector3.dot(line_start, plane_n)
        # bd = Vector3.dot(line_end, plane_n)
        # t = (-plane_d - ad)/(bd-ad)
        # line_vec = line_end - line_start
        # line_to_intersect = line_vec*t
        # return line_start + line_to_intersect

    def _clip_against_plane(self, plane_p, plane_n, triangle):
        """
        Clip the triangle against the plane and returns the number of valid triangles inside.
        Also returns one or two triangles that are guaranteed to be inside.
        """
        # plane_n.normalize()

        # inside_points = np.empty(3, dtype=Vector3)
        # outside_points = np.empty(3, dtype=Vector3)
        # n_inside_points = 0
        # n_outside_points = 0

        # d0 = triangle.p[0].distance_to_plane(plane_p, plane_n)
        # d1 = triangle.p[1].distance_to_plane(plane_p, plane_n)
        # d2 = triangle.p[2].distance_to_plane(plane_p, plane_n)

        # if (d0 >= 0):
        #     inside_points[n_inside_points] = triangle.p[0]
        #     n_inside_points += 1
        # else:
        #     outside_points[n_outside_points] = triangle.p[0]
        #     n_inside_points += 1
        # if (d1 >= 0):
        #     inside_points[n_inside_points] = triangle.p[1]
        #     n_inside_points += 1
        # else:
        #     outside_points[n_outside_points] = triangle.p[1]
        #     n_inside_points += 1
        # if (d2 >= 0):
        #     inside_points[n_inside_points] = triangle.p[2]
        #     n_inside_points += 1
        # else:
        #     outside_points[n_outside_points] = triangle.p[2]
        #     n_inside_points += 1

        # if (n_inside_points == 0):
        #     # Completely clipped
        #     return 0, None, None

        # if n_inside_points == 3:
        #     # Not clipped at all
        #     return 1, triangle, None

        # if (n_inside_points == 1 and n_outside_points == 2):
        #     # Two points on the outside => We just make the triangle smaller
        #     new_triangle = triangle
        #     new_triangle.p[0] = inside_points[0]
        #     new_triangle.p[1] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])
        #     new_triangle.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[1])

        #     return 1, new_triangle, None

        # if (n_inside_points == 2 and n_outside_points == 1):
        #     # Two points inside, we have a quad that we need to triangulate
        #     new_triangle1 = triangle
        #     new_triangle1.p[0] = inside_points[0]
        #     new_triangle1.p[1] = inside_points[1]
        #     new_triangle1.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[0], outside_points[0])

        #     new_triangle2 = triangle
        #     new_triangle1.p[0] = inside_points[1]
        #     new_triangle1.p[1] = new_triangle1.p[2]
        #     new_triangle1.p[2] = self._line_plane_intersection(plane_p, plane_n, inside_points[1], outside_points[0])

        #     return 2, new_triangle1, new_triangle2

    def _adjust_lightness(self, color, amount=0.5):
        color_hls = colorsys.rgb_to_hls(*mc.to_rgb(color))
        return colorsys.hls_to_rgb(color_hls[0], max(0, min(1, amount*color_hls[1])), color_hls[2])


def main():
    r = Renderer(width=200, height=200, frame_time=0)
    engine3d = Engine3D(aspect_ratio=r.WIDTH/r.HEIGHT)

    theta = 0

    while True:
        engine3d.update(r)
        r.draw()

        # Crosshair
        r.line(-2, 0, 2, 0, width=1, color="red")
        r.line(0, -2, 0, 2, width=1, color="red")

        theta += 0.1


main()
# cProfile.run("main()", sort="time")