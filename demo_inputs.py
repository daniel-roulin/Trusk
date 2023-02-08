from renderer import Renderer

def main():
    r = Renderer(width=100, height=100, target_fps=30)
    y = 50
    x = 50
    while True:
        if r.is_key_pressed("w"):
            y += 2
        if r.is_key_pressed("s"):
            y -= 2
        if r.is_key_pressed("d"):
            x += 2
        if r.is_key_pressed("a"):
            x -= 2

        if r.is_button_pressed(r.Button.LEFT):
            print("left")

        if r.is_button_pressed(r.Button.RIGHT):
            print("right")

        r.filled_triangle(x - 5, y - 5, x + 5, y - 5, x, y + 5, color="orange")
        r.filled_triangle(r.mouse_x - 5, r.mouse_y - 5, r.mouse_x + 5, r.mouse_y - 5, r.mouse_x, r.mouse_y + 5, color="blue")
        r.draw()
        
        
if __name__ == "__main__":
    main()