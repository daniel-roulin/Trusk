from renderer import Renderer
import numpy as np
import matplotlib.colors as mc
import colorsys
from matrix import Matrix4x4


def lerp(a, b, t):
    return a*(1-t) + b*t


class Entity():
    def __init__(self, mesh=[], position=[0, 0, 0], color="#ffa75e"):
        # Adding 4th dimension to all vectors
        for triangle in mesh:
            for point in triangle:
                if len(point) == 3:
                    point.append(1)

        self.mesh = np.array(mesh, dtype=float)
        self.position = position
        self.color = color
        self.target_position = position
        # Should calculate normals here

    def translation_matrix(self):
        return Matrix4x4.translation(self.position[0], self.position[1], self.position[2])

    def animate(self, speed):
        self.position[0] = lerp(self.position[0], self.target_position[0], speed)
        self.position[1] = lerp(self.position[1], self.target_position[1], speed)
        self.position[2] = lerp(self.position[2], self.target_position[2], speed)


class Camera():
    def __init__(
        self,
        aspect_ratio=1,
        fov=80,
        near_clipping_plane=0.1,
        far_clipping_plane=1000,
        position=[0, 0, 2],
        direction=[0, 0, -1],
        orthographic_projection=False,
    ):
        self.aspect_ratio = aspect_ratio
        self.fov = fov
        self.near_clipping_plane = near_clipping_plane
        self.far_clipping_plane = far_clipping_plane
        self.position = position
        self.direction = direction
        self.orthographic_projection = orthographic_projection

    def view_matrix(self):
        norm_direction = self.direction/np.linalg.norm(self.direction)
        target = self.position + norm_direction
        up = np.array([0, 1, 0], dtype=float)
        camera_matrix = Matrix4x4.point_at(self.position, target, up)
        return np.linalg.inv(camera_matrix)

    def projection_matrix(self):
        return Matrix4x4.projection(
            self.fov,
            self.aspect_ratio,
            self.near_clipping_plane,
            self.far_clipping_plane,
        )


class Engine3D():
    # Referential: [left/right, up/down, front/back]
    def __init__(
        self,
        aspect_ratio=1,
        fov=80,
        near_clipping_plane=0.1,
        far_clipping_plane=1000,
        camera_position=[0, 0, 2],
        camera_direction=[0, 0, -1],
        light_direction=[-1, -2, 0],
        orthographic_projection=False,
    ):
        self.light_direction = light_direction

        self.camera = Camera(
            aspect_ratio,
            fov,
            near_clipping_plane,
            far_clipping_plane,
            camera_position,
            camera_direction,
            orthographic_projection,
        )

        # Entities list
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def update(self, renderer: Renderer):
        for entity in self.entities:
            triangles = entity.mesh

            # Computing normals
            line1 = triangles[:, 1, :3] - triangles[:, 0, :3]
            line2 = triangles[:, 2, :3] - triangles[:, 0, :3]
            normals = np.cross(line1, line2)
            normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]

            # Calculate dot product of normal and camera ray for all triangles
            camera_rays = triangles[:, 0, :3] - self.camera.position

            # Dark stackoverflow magic to simply perform a dot product
            # (Source: https://stackoverflow.com/questions/63301019/dot-product-of-two-numpy-arrays-with-3d-vectors)
            visibility_dot_products = np.einsum('ij,ij->i', normals, camera_rays)

            # Filter out triangles that are not visible
            visible_triangles = triangles[visibility_dot_products < 0]

            # Translation
            translated_triangles = visible_triangles @ entity.translation_matrix()

            # We move the triangles in front of the camera
            viewed_triangles = translated_triangles @ self.camera.view_matrix()

            # Alignment of the triangles normals with the light
            self.light_direction /= np.linalg.norm(self.light_direction)
            light_dot_product = np.dot(-self.light_direction, normals[visibility_dot_products < 0].T)

            # Can be greatly optimized by adjusting lightness manually
            colors = np.empty((viewed_triangles.shape[0], 3))
            for i in range(viewed_triangles.shape[0]):
                colors[i] = np.array(self.adjust_lightness(entity.color, (light_dot_product[i] + 1)/2.5))

            # We project the triangles: we "squish" them triangles onto the screen
            if not self.camera.orthographic_projection:
                projected_triangles = viewed_triangles @ self.camera.projection_matrix()
            else:
                projected_triangles = viewed_triangles

            projected_triangles[:, 0] /= projected_triangles[:, 0][:, np.newaxis, -1]
            projected_triangles[:, 1] /= projected_triangles[:, 1][:, np.newaxis, -1]
            projected_triangles[:, 2] /= projected_triangles[:, 2][:, np.newaxis, -1]
            projected_triangles[:, :, :2] *= np.array([renderer.WIDTH/2, renderer.HEIGHT/2])[np.newaxis, :]

            if not self.camera.orthographic_projection:
                projected_triangles[:, :, :2] *= np.array([-1, -1])[np.newaxis, :]

            for i in range(projected_triangles.shape[0]):
                t = projected_triangles[i]
                renderer.filled_triangle(t[0, 0], t[0, 1], t[1, 0], t[1, 1], t[2, 0], t[2, 1], color=colors[i])

    def adjust_lightness(self, color, amount=0.5):
        color_hls = colorsys.rgb_to_hls(*mc.to_rgb(color))
        return colorsys.hls_to_rgb(color_hls[0], max(0, min(1, amount*color_hls[1])), color_hls[2])
