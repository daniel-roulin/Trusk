class vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class triangle():
    def __init__(self, points):
        self.p = points
        self.sym = ""
        self.col = 0
        self.z = 0
        
class mesh():
    def __init__(self, triangles):
        self.triangles = triangles
        
class matrix4x4():
    def __init__(self):
        self.m = [[0, 0, 0, 0], 
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]
        
def get_object_from_file(filename):
    vertex, faces = [], []
    with open(filename) as f:
        for line in f:
            if line.startswith('v '):
                vertex_ = [float(i) for i in line.split()[1:]]
                vertex__ = vector3(vertex_[0], vertex_[1], vertex_[2])
                vertex.append(vertex__)
            elif line.startswith('f '):
                faces.append([int(i) for i in line.split()[1:]])
    
    triangles = []
    for tri in faces:
        print(tri)
        triangle_ = triangle([vertex[tri[0] - 1], vertex[tri[1] - 1], vertex[tri[2] - 1]])
        triangles.append(triangle_)
        
    return mesh(triangles)

get_object_from_file("resources/t_34_obj.obj")









