import numpy as np

matProj = np.zeros((4, 4))

height = 200
width = 200
near = 0.1
far = 1000
fov = 90
aspectRatio = (height/width)
fovRad = 1 / np.tan(fov * 0.5 / 180 * 3.14159265359)

matProj[0][0] = aspectRatio * fovRad
matProj[1][1] = fovRad
matProj[2][2] = far / (far -near)
matProj[3][2] = (-far * near) / (far - near)
matProj[2][3] = 1
matProj[3][3] = 0

print(matProj)

def MultiplyMatrixVector(vector, matrix):
    result = vector * matrix
    w = vector[0] * matrix[0][3] + vector[1] * matrix[1][3] + vector[2] * matrix[2][3] + matrix[3][3]
    
    if(w != 0):
        result[0] /= w
        result[1] /= w
        result[2] /= w
        
    return result
        
        