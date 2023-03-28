from renderer import Renderer
import numpy as np
import matplotlib.colors as mc
import colorsys
import cProfile
from matrix import Matrix4x4


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
        self.mesh = Mesh.load_from_file("t_34_obj.obj")
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
        self.camera_position = np.array([0, 3, 3], dtype=float)

        self.look_direction = np.array([0, 0, 1], dtype=float)
        self.look_direction /= np.linalg.norm(self.look_direction)

        self.light_direction = np.array([0, 1, 1], dtype=float)
        self.light_direction /= np.linalg.norm(self.light_direction)

        self.projection_matrix = Matrix4x4.projection(80, aspect_ratio, 0.1, 1000)

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

        ##########################################################################

        up = np.array([0, 1, 0], dtype=float)
        # target = np.array([0, 0, 1], dtype=float)

        # mcamera_rotation = Matrix4x4.rotationY(self.fyaw)
        # self.vlookdir = vtarget*mcamera_rotation

        self.camera_position = np.array([np.cos(theta)*4, 2, np.sin(theta)*4])
        self.look_direction = self.camera_position + np.array([0, -3, 0])

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
        projected_triangles[:, :, :2] += np.array([1, 1])[np.newaxis, :]
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
    renderer = Renderer(width=200, height=200, target_fps=60)
    engine3d = Engine3D(aspect_ratio=renderer.WIDTH/renderer.HEIGHT)

    theta = 0

    while True:
        engine3d.update(renderer, theta)
        renderer.draw()

        theta += 0.1


main()
# cProfile.run("main()", sort="time")