from __future__ import annotations
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

    def __mul__(a, b: Vector3 | Matrix4x4) -> Vector3:
        if isinstance(b, Vector3):
            result = Vector3(0, 0, 0)
            result.vector = a.vector*b
            return result
        if isinstance(b, Matrix4x4):
            result = Vector3(0, 0, 0)
            result.vector = a.vector @ b.matrix

            #TODO: Comprendre d'ou vient ce truc bizzare
            if (result.w != 0.0):
                result.x /= result.w
                result.y /= result.w
                result.z /= result.w

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
        result.vector = np.empty(4, dtype=float)
        result.vector[0:3] = np.cross(a.vector[:-1], b.vector[:-1])
        result.vector[3] = 1
        return result

    def distance_to_plane(self, plane_p: Vector3, plane_n: Vector3) -> float:
        plane_n.normalize()
        return (plane_n.x*self.x + plane_n.y*self.y + plane_n.z*self.z - Vector3.dot(plane_n, plane_p))


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

    def __mul__(a, b: Matrix4x4) -> Matrix4x4:
        return a.matrix @ b.matrix

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

        fov_rad = 1/np.tan(fov*0.5/180.0*np.pi)
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


def multiplyMatrixVector(i, m):
    result = Vector3(0, 0, 0)
    result.x = i.x*m.matrix[0][0] + i.y*m.matrix[1][0] + i.z*m.matrix[2][0] + m.matrix[3][0]
    result.y = i.x*m.matrix[0][1] + i.y*m.matrix[1][1] + i.z*m.matrix[2][1] + m.matrix[3][1]
    result.z = i.x*m.matrix[0][2] + i.y*m.matrix[1][2] + i.z*m.matrix[2][2] + m.matrix[3][2]

    w = i.x*m.matrix[0][3] + i.y*m.matrix[1][3] + i.z*m.matrix[2][3] + m.matrix[3][3]

    if (w != 0.0):
        result.x /= w
        result.y /= w
        result.z /= w

    return result


if __name__ == "__main__":
    a = Matrix4x4()
    a.projection(80, 1, 0.1, 1000)

    b = Vector3(0.49757104789172696, 0.7506020846263005, -29.565236198776184, 1.0)

    print(multiplyMatrixVector(b, a))
    print(b*a)
