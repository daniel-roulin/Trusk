from __future__ import annotations
import numpy as np


class Vector3():
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 1) -> None:
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
        result = Vector3()
        result.vector[0:3] = a.vector[0:3] - b.vector[0:3]
        return result

    def __add__(a, b: Vector3) -> Vector3:
        result = Vector3()
        result.vector[0:3] = a.vector[0:3] + b.vector[0:3]
        return result

    def __mul__(a, b: float | Matrix4x4) -> Vector3:
        if isinstance(b, float):
            result = Vector3()
            result.vector[0:3] = a.vector[0:3]*b
            return result
        if isinstance(b, Matrix4x4):
            result = Vector3()
            result.vector = a.vector @ b.matrix
            return result

    def multiply_with_matrix(self, matrix: Matrix4x4):
        # Only case where we use w
        self.vector = self.vector @ matrix.matrix

    def multiply_with_number(self, number: float):
        self.vector[0:3] = self.vector[0:3]*number

    def __truediv__(a, b: Vector3) -> Vector3:
        result = Vector3()
        result.vector[0:3] = a.vector[0:3]/b
        return result

    def length(self) -> float:
        return np.linalg.norm(self.vector[0:3])

    def normalize(self) -> None:
        l = self.length()
        self.vector[0:3] /= l

    def dot(a, b: Vector3) -> float:
        return np.dot(a.vector[0:3], b.vector[0:3])

    def cross(a, b: Vector3) -> Vector3:
        result = Vector3()
        result.vector[0:3] = np.cross(a.vector[0:3], b.vector[0:3])
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

    def __mul__(a, b: Matrix4x4) -> Matrix4x4:
        return a.matrix @ b.matrix

    def inverse(self) -> None:
        try:
            self.matrix = np.linalg.inv(self.matrix)
        except np.linalg.LinAlgError as e:
            raise ValueError("This matrix has no inverse!")

    def identity() -> Matrix4x4:
        result = Matrix4x4()
        result.matrix[0][0] = 1
        result.matrix[1][1] = 1
        result.matrix[2][2] = 1
        result.matrix[3][3] = 1
        return result

    def rotationX(angle: float) -> Matrix4x4:
        """
        Args:
            angle: Angle must be in radian!
        """
        result = Matrix4x4()
        result.matrix[0][0] = 1
        result.matrix[1][1] = np.cos(angle)
        result.matrix[1][2] = np.sin(angle)
        result.matrix[2][1] = -np.sin(angle)
        result.matrix[2][2] = np.cos(angle)
        result.matrix[3][3] = 1
        return result

    def rotationY(angle: float) -> Matrix4x4:
        """
        Args:
            angle: Angle must be in radian!
        """
        result = Matrix4x4()
        result.matrix[0][0] = np.cos(angle)
        result.matrix[0][2] = np.sin(angle)
        result.matrix[2][0] = -np.sin(angle)
        result.matrix[1][1] = 1
        result.matrix[2][2] = np.cos(angle)
        result.matrix[3][3] = 1
        return result

    def rotationZ(angle: float) -> Matrix4x4:
        """
        Args:
            angle: Angle must be in radian!
        """
        result = Matrix4x4()
        result.matrix[0][0] = np.cos(angle)
        result.matrix[0][1] = np.sin(angle)
        result.matrix[1][0] = -np.sin(angle)
        result.matrix[1][1] = np.cos(angle)
        result.matrix[2][2] = 1
        result.matrix[3][3] = 1
        return result

    def translation(x: float, y: float, z: float) -> Matrix4x4:
        result = Matrix4x4()
        result.matrix[0][0] = 1
        result.matrix[1][1] = 1
        result.matrix[2][2] = 1
        result.matrix[3][3] = 1
        result.matrix[3][0] = x
        result.matrix[3][1] = y
        result.matrix[3][2] = z
        return result

    def projection(fov: float, aspect_ratio: float, near: float, far: float) -> Matrix4x4:
        """
        Args:
            fov : Fov must be in degrees
        """
        result = Matrix4x4()
        fov_rad = 1/np.tan(fov*0.5/180.0*np.pi)
        result.matrix[0][0] = aspect_ratio*fov_rad
        result.matrix[1][1] = fov_rad
        result.matrix[2][2] = far/(far-near)
        result.matrix[3][2] = (-far*near)/(far-near)
        result.matrix[2][3] = 1
        result.matrix[3][3] = 0
        return result

    def point_at(pos: Vector3, target: Vector3, up: Vector3) -> Matrix4x4:
        result = Matrix4x4()

        new_forward = target - pos
        new_forward.normalize()

        a = new_forward*Vector3.dot(up, new_forward)
        new_up = up - a
        new_up.normalize()

        new_right = Vector3.cross(new_up, new_forward)

        result.matrix[0][0] = new_right.x
        result.matrix[0][1] = new_right.y
        result.matrix[0][2] = new_right.z
        result.matrix[0][3] = 0
        result.matrix[1][0] = new_up.x
        result.matrix[1][1] = new_up.y
        result.matrix[1][2] = new_up.z
        result.matrix[1][3] = 0
        result.matrix[2][0] = new_forward.x
        result.matrix[2][1] = new_forward.y
        result.matrix[2][2] = new_forward.z
        result.matrix[2][3] = 0
        result.matrix[3][0] = pos.x
        result.matrix[3][1] = pos.y
        result.matrix[3][2] = pos.z
        result.matrix[3][3] = 1

        return result


def multiplyMatrixVector(i, m):
    result = Vector3()
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
    # a = Matrix4x4()
    # a.projection(80, 1, 0.1, 1000)

    # b = Vector3(0.49757104789172696, 0.7506020846263005, -29.565236198776184, 1.0)

    # print(multiplyMatrixVector(b, a))
    # print(b*a)
    a = Vector3(1, 0, 0)
    # b = Matrix4x4.identity()
    print(a*2)
    print(a)
