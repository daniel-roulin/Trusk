import numpy as np
import math
import matplotlib.pyplot as plt
from renderer import Renderer  
from matrix import matrix_multiplication

width, height = 100, 100

angle = 0
cube_position = [0,0]
scale = 500
speed = 0.01
points = [n for n in range(8)]

points[0] = [[-1], [-1], [1]]
points[1] = [[1], [-1], [1]]
points[2] = [[1], [1], [1]]
points[3] = [[-1], [1], [1]]
points[4] = [[-1], [-1], [-1]]
points[5] = [[1], [-1], [-1]]
points[6] = [[1], [1], [-1]]
points[7] = [[-1], [1], [-1]]


def connect_point(i, j, k, r):
    a = k[i]
    b = k[j]
    r.line(a[0], a[1], b[0], b[1], color = "black", width = 0.5)
    
def connect_triangles(i, j, k, points, r):
    r.filled_triangle(points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1], color = "#33FFBC")

def render(r, angle):
    index = 0
    projected_points = [j for j in range(len(points))]

    rotation_x = [[1, 0, 0],
                  [0, math.cos(angle), -math.sin(angle)],
                  [0, math.sin(angle), math.cos(angle)]]

    rotation_y = [[math.cos(angle), 0, -math.sin(angle)],
                  [0, 1, 0],
                  [math.sin(angle), 0, math.cos(angle)]]

    rotation_z = [[math.cos(angle), -math.sin(angle), 0],
                  [math.sin(angle), math.cos(angle), 0],
                  [0, 0 ,1]]

    for point in points:
        rotated_2d = matrix_multiplication(rotation_y, point)
        rotated_2d = matrix_multiplication(rotation_x, rotated_2d)
        rotated_2d = matrix_multiplication(rotation_z, rotated_2d)
        distance = 5
        z = 1/(distance - rotated_2d[2][0])
        projection_matrix = [[z, 0, 0],
                            [0, z, 0]]
        projected_2d = matrix_multiplication(projection_matrix, rotated_2d)

        x = int(projected_2d[0][0] * scale) + cube_position[0]
        y = int(projected_2d[1][0] * scale) + cube_position[1]
        projected_points[index] = [x, y]
        #pygame.draw.circle(screen, blue, (x, y), 10)
        index += 1
    #draw edges
    for m in range(4):
        connect_point(m, (m+1)%4, projected_points, r)
        connect_point(m+4, (m+1)%4 + 4, projected_points, r)
        connect_point(m, m+4, projected_points, r)
        
    connect_triangles(m, (m+1) % 4, m+4, projected_points, r)
    connect_triangles((m+1) % 4, m+4, ((m+1) % 4) + 4, projected_points, r)

    
def main():
    r = Renderer(width=200, height=200, target_fps=60)
    angle = 1
    while True:
        angle += speed
        render(r, angle)
        r.draw()
        
main()
