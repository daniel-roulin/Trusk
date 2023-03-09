import numpy as np


class Vector():
    def __init__(self, x, y, z, w=1):
        self.vector = np.array([x, y, z, w])

    @property
    def x(self):
        return self.vector[0]

    @x.setter
    def x(self, value):
        self.vector[0] = value

    @property
    def y(self):
        return self.vector[1]

    @y.setter
    def y(self, value):
        self.vector[1] = value

    @property
    def z(self):
        return self.vector[2]

    @z.setter
    def z(self, value):
        self.vector[2] = value

    @property
    def w(self):
        return self.vector[3]

    @w.setter
    def w(self, value):
        self.vector[3] = value

    def __str__(self):
        return f"Vector({self.x}, {self.y}, {self.z}, {self.w})"

    def __sub__(a, b):
        result = Vector(0, 0, 0)
        result.vector = a.vector - b.vector
        return result

    def __add__(a, b):
        result = Vector(0, 0, 0)
        result.vector = a.vector + b.vector
        return result

    def __mul__(a, b):
        result = Vector(0, 0, 0)
        result.vector = a.vector*b
        return result

    def __truediv__(a, b):
        result = Vector(0, 0, 0)
        result.vector = a.vector/b
        return result

    def length(self):
        return np.linalg.norm(self.vector)

    def normalize(self):
        l: int = self.length()
        return self/l

    def dot(a, b) -> float:
        return np.dot(a.vector, b.vector)

    def cross(a, b):
        result = Vector(0, 0, 0)
        result.vector = np.cross(a.vector, b.vector)
        return result


class Triangle():
    def __init__(self, points):
        self.p = np.array([points])
        self.sym = ""
        self.col = 0


class Mesh():
    def __init__(self, triangles):
        self.triangles = np.array([triangles])

    def load_from_file(path):
        ...


class Matrix():
    def __init__(self):
        self.matrix = np.zeros((4, 4))

    # TODO: Operator overloading ?
    def multiply_with_vector(self, vector):
        return self.matrix @ vector.vector

    def identity(self):
        self.matrix[0][0] = 1
        self.matrix[1][1] = 1
        self.matrix[2][2] = 1
        self.matrix[3][3] = 1

    def rotationX(self, angle):
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

    def rotationY(self, angle):
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

    def rotationZ(self, angle):
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

    def translation(self, x, y, z):
        self.matrix[0][0] = 1
        self.matrix[1][1] = 1
        self.matrix[2][2] = 1
        self.matrix[3][3] = 1
        self.matrix[3][0] = x
        self.matrix[3][1] = y
        self.matrix[3][2] = z

    def projection(self, fov, aspect_ratio, near, far):
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

    def multiply_with_matrix(self, matrix):
        return self.matrix @ matrix.matrix

    def point_at(self, pos: Vector, target: Vector, up: Vector):
        new_forward = target - pos
        new_forward.normalize()

        a = new_forward*up.dot(new_forward)
        new_up = up - a
        new_up.normalize()

        new_right = new_up.cross(new_forward)

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


if __name__ == "__main__":
    a = Vector(0, 0, 0).dot()
