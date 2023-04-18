import time
from renderer import Renderer


def main():
    r = Renderer(width=100, height=100, target_fps=30)
    x1 = 50
    y1 = 50
    x2 = 50
    y2 = 50
    while True:
        if r.is_key_pressed("w"):
            y1 += 2
        if r.is_key_pressed("s"):
            y1 -= 2
        if r.is_key_pressed("d"):
            x1 += 2
        if r.is_key_pressed("a"):
            x1 -= 2

        if r.is_button_pressed(r.Button.LEFT):
            print("left")

        if r.is_button_pressed(r.Button.RIGHT):
            print("right")

        x2 += r.mouse_delta_x
        y2 += r.mouse_delta_y

        r.filled_triangle(x1 - 5, y1 - 5, x1 + 5, y1 - 5, x1, y1 + 5, color="orange")
        r.filled_triangle(r.mouse_x - 5, r.mouse_y - 5, r.mouse_x + 5, r.mouse_y - 5, r.mouse_x, r.mouse_y + 5, color="blue")
        r.filled_triangle(x2 - 5, y2 - 5, x2 + 5, y2 - 5, x2, y2 + 5, color="red")
        r.draw()


if __name__ == "__main__":
    main()