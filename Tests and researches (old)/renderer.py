from enum import IntEnum
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


class Renderer:
    class Button(IntEnum):
        LEFT = 1
        MIDDLE = 2
        RIGHT = 3

    def __init__(self, width=10, height=10, frame_time=1/60):
        """A class that abstracts the rendering engine"""
        self.WIDTH = width
        self.HEIGHT = height
        self.FRAME_TIME = frame_time

        self.fig, self.axes = plt.subplots()
        self._set_axis()
        self._setup_inputs()

    def _set_axis(self):
        self.axes.set_xlim(-200, self.WIDTH)
        self.axes.set_ylim(-200, self.HEIGHT)
        self.axes.set_axis_off()
        self.axes.set_aspect("equal", "box")

    def _setup_inputs(self):
        self._keys_pressed = []
        self._buttons_pressed = []
        self.mouse_x = 0
        self.mouse_y = 0
        self.prev_mouse_x = self.mouse_x
        self.prev_mouse_y = self.mouse_y
        self.mouse_delta_x = self.mouse_x - self.prev_mouse_x
        self.mouse_delta_y = self.mouse_y - self.prev_mouse_y
        for param in plt.rcParams.find_all("keymap"):
            plt.rcParams[param] = []
        plt.connect('key_press_event', self._key_pressed)
        plt.connect('key_release_event', self._key_released)
        plt.connect('motion_notify_event', self._mouse_moved)
        plt.connect('close_event', self.quit)
        plt.connect('button_press_event', self._button_pressed)
        plt.connect('button_release_event', self._button_released)

    def _key_pressed(self, event):
        self._keys_pressed.append(event.key)

    def _key_released(self, event):
        self._keys_pressed.remove(event.key)

    def _mouse_moved(self, event):
        if event.inaxes:
            self.mouse_x = event.xdata
            self.mouse_y = event.ydata
            self.mouse_delta_x = self.mouse_x - self.prev_mouse_x
            self.mouse_delta_y = self.mouse_y - self.prev_mouse_y
            self.prev_mouse_x = self.mouse_x
            self.prev_mouse_y = self.mouse_y

    def _button_pressed(self, event):
        self._buttons_pressed.append(event.button.value)

    def _button_released(self, event):
        self._buttons_pressed.remove(event.button.value)

    def quit(self, event):
        exit()

    def is_key_pressed(self, key):
        return key in self._keys_pressed

    def is_button_pressed(self, button):
        return button in self._buttons_pressed

    def draw(self):
        """Renders the scene."""
        plt.pause(0)
        # plt.pause(self.FRAME_TIME)
        self.axes.cla()
        self._set_axis()

    def point(self, x, y, color="orange"):
        """Sets the point (x, y) to the character char."""
        self.axes.plot(x, y, ".", color=color)

    def line(self, x1, y1, x2, y2, width=2, color="orange"):
        """Draws a line between the two points (x1, y1) (x2, y2)."""
        self.axes.plot([x1, x2], [y1, y2], color=color, linewidth=width)

    def text(self, x, y, s, color="orange"):
        """Write the text s starting at the x, y location on the screen."""
        self.axes.text(x, y, s, color=color)

    def rect(self, x, y, w, h, color="orange", width=2):
        """Draws a rectangle whose bottom left corner is at (x, y) and of width w and height h."""
        X = [x, x, x + w, x + w, x]
        Y = [y, y + h, y + h, y, y]
        self.axes.plot(X, Y, color=color, lw=width)

    def filled_rect(self, x, y, w, h, color="orange"):
        """Draws a filled rectangle whose bottom left corner is at (x, y) and of width w and height h."""
        X = [x, x, x + w, x + w]
        Y = [y, y + h, y + h, y]
        self.axes.fill(X, Y, color=color)

    def ellipse(self, x, y, w, h, color="orange", width=2):
        """Draws an ellipse of center (x, y) and of width h and height h."""
        ellipse = Ellipse((x, y), w, h, facecolor="none", edgecolor=color, linewidth=width)
        self.axes.add_artist(ellipse)

    def filled_ellipse(self, x, y, w, h, color="orange"):
        """Draws a filled ellipse of center (x, y) and of width h and height h."""
        ellipse = Ellipse((x, y), w, h, color=color)
        self.axes.add_artist(ellipse)

    def triangle(self, x1, y1, x2, y2, x3, y3, color="orange", width=2):
        """Draws a triangle from 3 points"""
        X = [x1, x2, x3, x1]
        Y = [y1, y2, y3, y1]
        self.axes.plot(X, Y, color=color, lw=width)

    def filled_triangle(self, x1, y1, x2, y2, x3, y3, color="orange"):
        """Draws a filled triangle from 3 points"""
        X = [x1, x2, x3]
        Y = [y1, y2, y3]
        self.axes.fill(X, Y, color=color)
