from __future__ import annotations
import numpy as np


class Matrix4x4():
    def identity():
        result = np.zeros((4, 4), dtype=float)
        result[0][0] = 1
        result[1][1] = 1
        result[2][2] = 1
        result[3][3] = 1
        return result

    def rotationX(angle: float):
        """
        Args:
            angle: Angle must be in radian!
        """
        result = np.zeros((4, 4), dtype=float)
        result[0][0] = 1
        result[1][1] = np.cos(angle)
        result[1][2] = np.sin(angle)
        result[2][1] = -np.sin(angle)
        result[2][2] = np.cos(angle)
        result[3][3] = 1
        return result

    def rotationY(angle: float):
        """
        Args:
            angle: Angle must be in radian!
        """
        result = np.zeros((4, 4), dtype=float)
        result[0][0] = np.cos(angle)
        result[0][2] = np.sin(angle)
        result[2][0] = -np.sin(angle)
        result[1][1] = 1
        result[2][2] = np.cos(angle)
        result[3][3] = 1
        return result

    def rotationZ(angle: float):
        """
        Args:
            angle: Angle must be in radian!
        """
        result = np.zeros((4, 4), dtype=float)
        result[0][0] = np.cos(angle)
        result[0][1] = np.sin(angle)
        result[1][0] = -np.sin(angle)
        result[1][1] = np.cos(angle)
        result[2][2] = 1
        result[3][3] = 1
        return result

    def translation(x: float, y: float, z: float):
        result = np.zeros((4, 4), dtype=float)
        result[0][0] = 1
        result[1][1] = 1
        result[2][2] = 1
        result[3][3] = 1
        result[3][0] = x
        result[3][1] = y
        result[3][2] = z
        return result

    def projection(fov: float, aspect_ratio: float, near: float, far: float):
        """
        Args:
            fov : Fov must be in degrees
        """
        result = np.zeros((4, 4), dtype=float)
        fov_rad = 1/np.tan(fov*0.5/180.0*np.pi)
        result[0][0] = aspect_ratio*fov_rad
        result[1][1] = fov_rad
        result[2][2] = far/(far-near)
        result[3][2] = (-far*near)/(far-near)
        result[2][3] = 1
        result[3][3] = 0
        return result

    def point_at(pos, target, up):
        result = np.zeros((4, 4), dtype=float)

        new_forward = target - pos
        new_forward /= np.linalg.norm(new_forward)

        a = new_forward*np.dot(up, new_forward)
        new_up = up - a
        new_up /= np.linalg.norm(new_up)

        new_right = np.cross(new_up, new_forward)

        result[0][0] = new_right[0]
        result[0][1] = new_right[1]
        result[0][2] = new_right[2]
        result[0][3] = 0
        result[1][0] = new_up[0]
        result[1][1] = new_up[1]
        result[1][2] = new_up[2]
        result[1][3] = 0
        result[2][0] = new_forward[0]
        result[2][1] = new_forward[1]
        result[2][2] = new_forward[2]
        result[2][3] = 0
        result[3][0] = pos[0]
        result[3][1] = pos[1]
        result[3][2] = pos[2]
        result[3][3] = 1

        return result