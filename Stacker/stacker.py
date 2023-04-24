""" 
Daniel Roulin
A simple stacker game
"""

import math
from renderer import Renderer
from engine import Engine3D, Entity
import colorsys
import numpy as np
import keyboard


def lerp(a, b, t):
    """Linear Interpolation

    Args:
        a (float): start
        b (float): end
        t (float): amount (percentage)

    Returns:
        float: A value between at t distnace between a and b
    """
    return a*(1-t) + b*t


class Stacker():
    def __init__(self):
        # The renderer is responsible for displaying basic shapes (triangles, rectangles, ...)
        self.renderer = Renderer(
            width=200,
            height=200,
            frame_time=0,
        )

        # The 3D Engine can draw more advance 3 dimensional entities, like cubes, 3d models, icospheres, ...
        self.engine3d = Engine3D()
        self.engine3d.light_direction = [-1, -2, 0]
        self.engine3d.camera.aspect_ratio = self.renderer.WIDTH/self.renderer.HEIGHT
        self.engine3d.camera.orthographic_projection = True
        self.engine3d.camera.position = [1.5, 1.5, 1.5]
        self.engine3d.camera.direction = [-1, -1, -1]
        self.engine3d.camera.light_direction = [-1, -2, 0]

        # The direction in which the platform is currently moving
        self.direction = np.array([1, 0, 0])

        # The target position of the camera, allows smooth camera movements and animations using lerp
        self.camera_target_pos = self.engine3d.camera.position.copy()

        # The caracteristics of the initial platform
        self.platform_width = 1
        self.platform_depth = 1
        self.platform_rest_position = np.zeros(3)

        # Preparing the stack
        self.platforms = []
        for i in range(11):
            self.drop_platform()

        # Game logic variables
        self.time = 0
        self.space_already_pressed = False
        self.gameover = False

    def create_box(self, x, y, z, w, h, d):
        """Return a box entity.
        Takes the position of the back lower left vertex and the width, height and depth of the box.

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate
            w (float): Width
            h (float): Height
            d (float): Depth
        """
        p1 = [0, 0, 0]
        p2 = [w, 0, 0]
        p3 = [0, h, 0]
        p4 = [w, h, 0]
        p5 = [0, 0, d]
        p6 = [w, 0, d]
        p7 = [0, h, d]
        p8 = [w, h, d]
        mesh = [
            # Face de devant
            [p1, p3, p4],
            [p1, p4, p2],
            # Face de droite
            [p2, p4, p8],
            [p2, p8, p6],
            # Face arrière
            [p6, p8, p7],
            [p6, p7, p5],
            # Face de gauche
            [p5, p7, p3],
            [p5, p3, p1],
            # Face du haut
            [p3, p7, p8],
            [p3, p8, p4],
            # Face du bas
            [p6, p5, p1],
            [p6, p1, p2],
        ]
        cube = Entity(mesh=mesh, position=[x, y, z])
        return cube

    def drop_platform(self):
        """Drop a platform on the one below it and resize itself to fit on it.
        """
        if len(self.platforms) > 0:
            # The part of the plateform on the tower.
            self.platform_width = self.platform_width - abs(self.platforms[-1].position[0] - self.platform_rest_position[0])
            self.platform_depth = self.platform_depth - abs(self.platforms[-1].position[2] - self.platform_rest_position[2])

            # If we are no longer on the tower, we lost!
            if self.platform_width < 0 or self.platform_depth < 0:
                self.gameover = True
                self.camera_target_pos[1] -= 0.6
                return

            # Changing the resting position if we are in the negatives
            if self.platforms[-1].position[0] > self.platform_rest_position[0]:
                self.platform_rest_position[0] = self.platforms[-1].position[0]
            if self.platforms[-1].position[2] > self.platform_rest_position[2]:
                self.platform_rest_position[2] = self.platforms[-1].position[2]

            # Recreating a platform with the correct size
            self.engine3d.remove_entity(self.platforms[-1])
            self.platforms.remove(self.platforms[-1])
            self.add_platform()

            # The stack is growing!
            self.platform_rest_position[1] += 0.2

        # The new moving platform
        self.add_platform()

        # We reset the time of the cosinus, so the platform is far from the tower
        self.time = 0

        # We raise the camera
        self.camera_target_pos[1] += 0.2

        # We rotate the direction in which the platform is moving by 90 degrees
        self.direction = np.array([-self.direction[2], 0, self.direction[0]])

    def add_platform(self):
        """Add a platform to our list of platforms and to the 3d engine.
        """
        # We create a box of the correct shape and size
        platform = self.create_box(self.platform_rest_position[0], self.platform_rest_position[1], self.platform_rest_position[2], self.platform_width, 0.2, self.platform_depth)

        # By changing color space, we can change the hue of our color instead of the raw RGB values.
        platform.color = colorsys.hsv_to_rgb((len(self.platforms) % 100)/100, 1, 1)

        # We add our platform to our list of platforms and to the 3d engine
        self.platforms.append(platform)
        self.engine3d.add_entity(platform)

    def run(self):
        """The main loop of the game
        """
        while True:
            # We allow toggling between camera projection mode for the demonstration
            if keyboard.is_pressed("o"):
                self.engine3d.camera.orthographic_projection = True
            elif keyboard.is_pressed("p"):
                self.engine3d.camera.orthographic_projection = False

            if not self.gameover:
                # We check if space was pressde in this frame, and avoiding repeating inputs
                if keyboard.is_pressed("space"):
                    if not self.space_already_pressed:
                        self.drop_platform()
                    self.space_already_pressed = True
                else:
                    self.space_already_pressed = False

                # We animate the top platform
                self.time += 1/30
                self.platforms[-1].position = self.platform_rest_position + math.cos(self.time)*self.direction

                # We destroy platform that are too low to be visible
                for platform in self.platforms:
                    if platform.position[1] < self.engine3d.camera.position[1] - 5:
                        self.platforms.remove(platform)
                        self.engine3d.remove_entity(platform)

            # We smoothly move the camera to its target
            self.engine3d.camera.position[0] = lerp(self.engine3d.camera.position[0], self.camera_target_pos[0], 0.1)
            self.engine3d.camera.position[1] = lerp(self.engine3d.camera.position[1], self.camera_target_pos[1], 0.1)
            self.engine3d.camera.position[2] = lerp(self.engine3d.camera.position[2], self.camera_target_pos[2], 0.1)

            # We update the 3d engine and render the scene.
            self.engine3d.update(self.renderer)
            self.renderer.draw()
