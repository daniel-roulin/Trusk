import numpy as np
from math import *
import matplotlib.pyplot as plt
from renderer import Renderer  

angle = 1
scale = 100
circle_pos = [10, 10]

points = []
#Vertices of the cube
points.append(np.matrix([-1, -1, 1]))
points.append(np.matrix([1, -1, 1]))
points.append(np.matrix([1,  1, 1]))
points.append(np.matrix([-1, 1, 1]))
points.append(np.matrix([-1, -1, -1]))
points.append(np.matrix([1, -1, -1]))
points.append(np.matrix([1, 1, -1]))
points.append(np.matrix([-1, 1, -1]))

#projection matrix
projection_matrix = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])

projected_points = [
    [n, n] for n in range(len(points))
]

def connect_points(i, j, points, r):
    r.line(points[i][0], points[i][1], points[j][0], points[j][1], color = "black", width = 0.5)
    
def connect_triangles(i, j, k, points, r):
    r.filled_triangle(points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1], color = "#33FFBC")

def render(r, angle):
    rotation_z = np.matrix([
        [cos(angle), -sin(angle), 0],
        [sin(angle), cos(angle), 0],
        [0, 0, 1],
    ])

    rotation_y = np.matrix([
        [cos(angle * 0.1), 0, sin(angle * 0.1)],
        [0, 1, 0],
        [-sin(angle * 0.1), 0, cos(angle * 0.1)],
    ])

    rotation_x = np.matrix([
        [1, 0, 0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle), cos(angle)],
    ])
    
    i = 0
    for point in points:
        rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
        rotated2d = np.dot(rotation_y, rotated2d)
        rotated2d = np.dot(rotation_x, rotated2d)

        projected2d = np.dot(projection_matrix, rotated2d)

        x = int(projected2d[0][0] * scale) + circle_pos[0]
        y = int(projected2d[1][0] * scale) + circle_pos[1]

        projected_points[i] = [x, y]
        i += 1

    for p in range(4):
        connect_points(p, (p+1) % 4, projected_points, r)
        connect_points(p+4, ((p+1) % 4) + 4, projected_points, r)
        connect_points(p, (p+4), projected_points, r)
        

    connect_triangles(p, (p+1) % 4, p+4, projected_points, r)
    connect_triangles((p+1) % 4, p+4, ((p+1) % 4) + 4, projected_points, r)
        #connect_triangles(p + 4, ((p+1) % 4) + 4, (p+1) % 4, projected_points, r)
        
def main():
    r = Renderer(width=200, height=200, target_fps=30)
    angle = 1
    while True:
        angle -= 0.1
        render(r, angle)
        r.draw()
        
main()
