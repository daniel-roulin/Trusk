from __future__ import annotations
from collections.abc import Iterable
import numpy as np


class Vector3():
    def __init__(self, x: float, y: float, z: float, w=1) -> None:
        self.vector = np.array([x, y, z, w], dtype=float)

    @property
    def x(self) -> float:
        return self.vector[0]

    @x.setter
    def x(self, value: float) -> None:
        self.vector[0] = value

    @property
    def y(self) -> float:
        return self.vector[1]

    @y.setter
    def y(self, value: float) -> None:
        self.vector[1] = value

    @property
    def z(self) -> float:
        return self.vector[2]

    @z.setter
    def z(self, value: float) -> None:
        self.vector[2] = value

    @property
    def w(self) -> float:
        return self.vector[3]

    @w.setter
    def w(self, value: float) -> None:
        self.vector[3] = value

    def __str__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z}, {self.w})"

    def __sub__(a, b: Vector3) -> Vector3:
        result = Vector3(0, 0, 0)
        result.vector = a.vector - b.vector
        return result

    def __add__(a, b: Vector3) -> Vector3:
        result = Vector3(0, 0, 0)
        result.vector = a.vector + b.vector
        return result

    def __mul__(a, b: Vector3) -> Vector3:
        result = Vector3(0, 0, 0)
        result.vector = a.vector*b
        return result

    def __truediv__(a, b: Vector3) -> Vector3:
        result = Vector3(0, 0, 0)
        result.vector = a.vector/b
        return result

    def length(self) -> float:
        return np.linalg.norm(self.vector)

    def normalize(self) -> None:
        l = self.length()
        self = self/l

    def dot(a, b: Vector3) -> float:
        return np.dot(a.vector, b.vector)

    def cross(a, b: Vector3) -> Vector3:
        result = Vector3(0, 0, 0)
        result.vector = np.cross(a.vector, b.vector)
        return result

    def distance_to_plane(self, plane_p: Vector3, plane_n: Vector3) -> float:
        plane_n.normalize()
        return (plane_n.x*self.x + plane_n.y*self.y + plane_n.z*self.z - Vector3.dot(plane_n, plane_p))


class Triangle():
    def __init__(self, points: Iterable[Vector3]) -> None:
        self.p = np.array(points, dtype=Vector3)
        self.sym = ""
        self.col = 0


class Mesh():
    def __init__(self, triangles: Iterable[Triangle]) -> None:
        self.triangles = np.array(triangles, dtype=Triangle)

    def load_from_file(path: str) -> None:
        ...


class Matrix4x4():
    def __init__(self) -> None:
        self.matrix = np.zeros((4, 4), dtype=float)

    def __str__(self) -> str:
        return "Matrix4x4:\n " + str(self.matrix)[1:-1]

    def __getitem__(self, key: int) -> np.ndarray:
        return self.matrix[key]

    def __setitem__(self, key: int, value: float) -> None:
        self.matrix[key] = value

    def identity(self) -> None:
        self.matrix[0][0] = 1
        self.matrix[1][1] = 1
        self.matrix[2][2] = 1
        self.matrix[3][3] = 1

    def __mul__(a, b: Matrix4x4 | Vector3) -> Matrix4x4 | Vector3:
        if isinstance(b, Matrix4x4):
            return a.matrix @ b.matrix
        if isinstance(b, Vector3):
            return a.matrix @ b.vector

    def inverse(self) -> None:
        try:
            self.matrix = np.linalg.inv(self.matrix)
        except np.linalg.LinAlgError as e:
            raise ValueError("This matrix has no inverse!")

    def rotationX(self, angle: float) -> None:
        """
        Args:
            angle: Angle must be in radian!
        """
        self.matrix[0][0] = 1
        self.matrix[1][1] = np.cos(angle)
        self.matrix[1][2] = np.sin(angle)
        self.matrix[2][1] = -np.sin(angle)
        self.matrix[2][2] = np.cos(angle)
        self.matrix[3][3] = 1

    def rotationY(self, angle: float) -> None:
        """
        Args:
            angle: Angle must be in radian!
        """
        self.matrix[0][0] = np.cos(angle)
        self.matrix[0][2] = np.sin(angle)
        self.matrix[2][0] = -np.sin(angle)
        self.matrix[1][1] = 1
        self.matrix[2][2] = np.cos(angle)
        self.matrix[3][3] = 1

    def rotationZ(self, angle: float) -> None:
        """
        Args:
            angle: Angle must be in radian!
        """
        self.matrix[0][0] = np.cos(angle)
        self.matrix[0][1] = np.sin(angle)
        self.matrix[1][0] = -np.sin(angle)
        self.matrix[1][1] = np.cos(angle)
        self.matrix[2][2] = 1
        self.matrix[3][3] = 1

    def translation(self, x: float, y: float, z: float) -> None:
        self.matrix[0][0] = 1
        self.matrix[1][1] = 1
        self.matrix[2][2] = 1
        self.matrix[3][3] = 1
        self.matrix[3][0] = x
        self.matrix[3][1] = y
        self.matrix[3][2] = z

    def projection(self, fov: float, aspect_ratio: float, near: float, far: float) -> None:
        """
        Args:
            fov : Fov must be in degrees
        """

        fov_rad = 1/np.tan(np.deg2rad(fov/2))
        self.matrix[0][0] = aspect_ratio*fov_rad
        self.matrix[1][1] = fov_rad
        self.matrix[2][2] = far/(far-near)
        self.matrix[3][2] = (-far*near)/(far-near)
        self.matrix[2][3] = 1
        self.matrix[3][3] = 0

    def point_at(self, pos: Vector3, target: Vector3, up: Vector3) -> None:
        new_forward = target - pos
        new_forward.normalize()

        a = new_forward*Vector3.dot(up, new_forward)
        new_up = up - a
        new_up.normalize()

        new_right = Vector3.cross(new_up, new_forward)

        self.matrix[0][0] = new_right.x
        self.matrix[0][1] = new_right.y
        self.matrix[0][2] = new_right.z
        self.matrix[0][3] = 0
        self.matrix[1][0] = new_up.x
        self.matrix[1][1] = new_up.y
        self.matrix[1][2] = new_up.z
        self.matrix[1][3] = 0
        self.matrix[2][0] = new_forward.x
        self.matrix[2][1] = new_forward.y
        self.matrix[2][2] = new_forward.z
        self.matrix[2][3] = 0
        self.matrix[3][0] = pos.x
        self.matrix[3][1] = pos.y
        self.matrix[3][2] = pos.z
        self.matrix[3][3] = 1


#TODO: move in other file
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