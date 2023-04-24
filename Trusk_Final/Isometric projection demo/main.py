from renderer import Renderer
import numpy as np
import matplotlib.colors as mc
import colorsys
from matrix import Matrix4x4
import sys
sys.path.append("J:\Pymodules")
import keyboard


class Mesh():
    def __init__(self, triangles) -> None:
        self.triangles = np.array(triangles, dtype=float)


class Engine3D():
    def __init__(self, aspect_ratio) -> None:
        self.mesh = Mesh(
            [
                # Face de devant ?
                [[0, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]],
                [[0, 0, 0, 1], [1, 1, 0, 1], [1, 0, 0, 1]],

                # Face de droite ?
                [[1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1]],
                [[1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1]],

                # Face arrière ?
                [[1, 0, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]],
                [[1, 0, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1]],

                # Face de gauche ?
                [[0, 0, 1, 1], [0, 1, 1, 1], [0, 1, 0, 1]],
                [[0, 0, 1, 1], [0, 1, 0, 1], [0, 0, 0, 1]],

                # Face du haut
                [[0, 1, 0, 1], [0, 1, 1, 1], [1, 1, 1, 1]],
                [[0, 1, 0, 1], [1, 1, 1, 1], [1, 1, 0, 1]],

                # Face du bas
                [[1, 0, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]],
                [[1, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]],
            ]
        )
        ### View parameters ###
        # Opposite to actual light source, if parallel to normal, dot product = 1
        self.light_direction = np.array([1, 2, 0], dtype=float)
        self.camera_position = np.array([1.5, 1.5, 1.5], dtype=float)
        self.look_direction = np.array([1, 1, 1], dtype=float)

        self.ORTHOGRAPHIC_PROJECTION = True
        self.projection_matrix = Matrix4x4.projection(80, aspect_ratio, 0.1, 1000)
        ### ###

        # Normalizing directions
        self.light_direction /= np.linalg.norm(self.light_direction)
        self.look_direction /= np.linalg.norm(self.look_direction)

        # Setting up the view matrix
        target = self.camera_position + self.look_direction
        up = np.array([0, 1, 0], dtype=float)
        self.camera_matrix = Matrix4x4.point_at(self.camera_position, target, up)
        self.view_matrix = np.linalg.inv(self.camera_matrix)

    # @timeit
    def update(self, r: Renderer):
        if keyboard.is_pressed("o"):
            self.ORTHOGRAPHIC_PROJECTION = True
        elif keyboard.is_pressed("p"):
            self.ORTHOGRAPHIC_PROJECTION = False

        triangles = self.mesh.triangles

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

        # Alignment of the triangles normals with the light
        light_dot_product = np.dot(self.light_direction, normals[visibility_dot_products < 0].T)

        # Can be greatly optimized by adjusting lightness manually
        colors = np.empty((viewed_triangles.shape[0], 3))
        for i in range(viewed_triangles.shape[0]):
            colors[i] = np.array(self._adjust_lightness("#ffa75e", (light_dot_product[i] + 1)/2.5))

        # We project the triangles: we "squish" them triangles onto the screen
        if not self.ORTHOGRAPHIC_PROJECTION:
            projected_triangles = viewed_triangles @ self.projection_matrix
        else:
            projected_triangles = viewed_triangles

        projected_triangles[:, 0] /= projected_triangles[:, 0][:, np.newaxis, -1]
        projected_triangles[:, 1] /= projected_triangles[:, 1][:, np.newaxis, -1]
        projected_triangles[:, 2] /= projected_triangles[:, 2][:, np.newaxis, -1]
        projected_triangles[:, :, :2] *= np.array([r.WIDTH/2, r.HEIGHT/2])[np.newaxis, :]

        if not self.ORTHOGRAPHIC_PROJECTION:
            projected_triangles[:, :, :2] *= np.array([-1, -1])[np.newaxis, :]

        for i in range(projected_triangles.shape[0]):
            t = projected_triangles[i]
            r.filled_triangle(t[0, 0], t[0, 1], t[1, 0], t[1, 1], t[2, 0], t[2, 1], color=colors[i])

    def _adjust_lightness(self, color, amount=0.5):
        color_hls = colorsys.rgb_to_hls(*mc.to_rgb(color))
        return colorsys.hls_to_rgb(color_hls[0], max(0, min(1, amount*color_hls[1])), color_hls[2])


def main():
    r = Renderer(width=200, height=200, frame_time=0)
    engine3d = Engine3D(aspect_ratio=r.WIDTH/r.HEIGHT)

    while True:
        engine3d.update(r)
        r.draw()

        # Crosshair
        # r.line(-2, 0, 2, 0, width=1, color="red")
        # r.line(0, -2, 0, 2, width=1, color="red")


main()