from renderer import Renderer
from engine import Engine3D, Entity


def create_box(x, y, z, w, h, d):
    """Returns a box entity.
    Takes the position of the back lower left vertex and the width, height and depth of the box.

    Args:
        x (float): X coordinate
        y (float): Y coordinate
        z (float): Z coordinate
        w (float): Width
        h (float): Height
        d (float): Depth
    """
    p1 = [x, y, z]
    p2 = [x + w, y, z]
    p3 = [x, y + h, z]
    p4 = [x + w, y + h, z]
    p5 = [x, y, z + d]
    p6 = [x + w, y, z + d]
    p7 = [x, y + h, z + d]
    p8 = [x + w, y + h, z + d]
    mesh = [
        # Face de devant ?
        [p1, p3, p4],
        [p1, p4, p2],

        # Face de droite ?
        [p2, p4, p8],
        [p2, p8, p6],

        # Face arrière ?
        [p6, p8, p7],
        [p6, p7, p5],

        # Face de gauche ?
        [p5, p7, p3],
        [p5, p3, p1],

        # Face du haut
        [p3, p7, p8],
        [p3, p8, p4],

        # Face du bas
        [p6, p5, p1],
        [p6, p1, p2],
    ]
    cube = Entity(mesh=mesh)
    return cube


def main():
    renderer = Renderer(
        width=200,
        height=200,
        frame_time=0,
    )

    engine3d = Engine3D()
    engine3d.light_direction = [-1, -2, 0]
    engine3d.camera.aspect_ratio = renderer.WIDTH/renderer.HEIGHT
    engine3d.camera.orthographic_projection = True
    engine3d.camera.position = [1.5, 1.5, 1.5]
    engine3d.camera.direction = [-1, -1, -1]
    engine3d.camera.light_direction = [-1, -2, 0]

    cube = create_box(0, 0, 0, 1, 1, 1)
    cube.color = "#FF0000"
    engine3d.add_entity(cube)

    while True:
        # engine3d.camera.position[1] += 0.1
        engine3d.light_direction[0] += 0.1
        cube.position[0] += 0.1
        engine3d.update(renderer)
        renderer.draw()


if __name__ == "__main__":
    main()