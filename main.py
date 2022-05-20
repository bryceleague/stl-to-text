import math
from re import X
import struct
import sys


class Object3d:
    def __init__(self, verts, norms):
        self.verts = verts
        self.norms = norms
    
    def from_stl(filename):
        (verts, norms) = read_stl(filename)
        return Object3d(verts, norms)

    def perspective(self, depth):
        for tri_n, tri in enumerate(self.verts):
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                fac = depth / (depth - z)
                self.verts[tri_n][vert_n] = x * fac, y * fac, z

    def scale(self, sx=1.0, sy=1.0, sz=1.0):
        for tri_n, tri in enumerate(self.verts):
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                self.verts[tri_n][vert_n] = x * sx, y * sy, z * sz

    def rot_x(self, rot):
        COS_RX = math.cos(rot)
        SIN_RX = math.sin(rot)
        for tri_n, (tri, norm) in enumerate(zip(self.verts, self.norms)):
            x, y, z = norm
            self.norms[tri_n] = x, y * COS_RX - z * SIN_RX, y * SIN_RX + z * COS_RX
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                self.verts[tri_n][vert_n] = x, y * COS_RX - z * SIN_RX, y * SIN_RX + z * COS_RX

    def rot_y(self, rot):
        COS_RY = math.cos(rot)
        SIN_RY = math.sin(rot)
        for tri_n, (tri, norm) in enumerate(zip(self.verts, self.norms)):
            x, y, z = norm
            self.norms[tri_n] = x * COS_RY + z * SIN_RY, y, z * COS_RY - x * SIN_RY
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                self.verts[tri_n][vert_n] = x * COS_RY + z * SIN_RY, y, z * COS_RY - x * SIN_RY

    def rot_z(self, rot):
        COS_RZ = math.cos(rot)
        SIN_RZ = math.sin(rot)
        for tri_n, (tri, norm) in enumerate(zip(self.verts, self.norms)):
            x, y, z = norm
            self.norms[tri_n] = x * COS_RZ - y * SIN_RZ, x * SIN_RZ + y * COS_RZ, z
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                self.verts[tri_n][vert_n] = x * COS_RZ - y * SIN_RZ, x * SIN_RZ + y * COS_RZ, z

    def translate(self, xt=0.0, yt=0.0, zt=0.0):
        for tri_n, tri in enumerate(self.verts):
            for vert_n, vert in enumerate(tri):
                x, y, z = vert
                self.verts[tri_n][vert_n] = x + xt, y + yt, z + zt
    
    def x_min(self):
        return min([vert[0] for tri in self.verts for vert in tri])
    
    def y_min(self):
        return min([vert[1] for tri in self.verts for vert in tri])
    
    def z_min(self):
        return min([vert[2] for tri in self.verts for vert in tri])
    
    def x_max(self):
        return max([vert[0] for tri in self.verts for vert in tri])
    
    def y_max(self):
        return max([vert[1] for tri in self.verts for vert in tri])
    
    def z_max(self):
        return max([vert[2] for tri in self.verts for vert in tri])

    def scale_to_fit(self, x_size, y_size):
        x = self.x_max() - self.x_min()
        y = self.y_max() - self.y_min()
        x_fac = x_size / x
        y_fac = y_size / y

        if x_fac < y_fac:
            self.scale(x_fac, x_fac, x_fac)
        else:
            self.scale(y_fac, y_fac, y_fac)

    def center(self):
        mid_x = (self.x_min() + self.y_max()) / 2
        mid_y = (self.x_min() + self.y_max()) / 2
        mid_z = (self.x_min() + self.y_max()) / 2

        self.translate(-mid_x, -mid_y, -mid_z)

class Scene:
    def __init__(self, objects, lighting, max_scr_x, min_scr_x, max_scr_y, min_scr_y):
        self.screenBuffer = [[(None, ' ') for _ in range(max_scr_x - min_scr_x)] for _ in range(max_scr_y - min_scr_y)]
        self.objects = objects
        self.lighting = lighting
        self.max_scr_x = max_scr_x
        self.min_scr_x = min_scr_x
        self.max_scr_y = max_scr_y
        self.min_scr_y = min_scr_y
    
    def create_trucated(objects, lighting):
        max_scr_x = math.ceil(max([obj.x_max() for obj in objects]))
        min_scr_x = math.floor(min([obj.x_min() for obj in objects]))
        max_scr_y = math.ceil(max([obj.y_max() for obj in objects]))
        min_scr_y = math.floor(min([obj.y_min() for obj in objects]))
        return Scene(objects, lighting, max_scr_x, min_scr_x, max_scr_y, min_scr_y)
    
    def clear_screen(self):
        self.screenBuffer = [[(None, ' ') for _ in range(self.max_scr_x - self.min_scr_x)] for _ in range(self.max_scr_y - self.min_scr_y)]

    def print(self):
        print('\n'.join([''.join([j[1] for j in i]) for i in self.screenBuffer]))
    
    def render(self):
        max_in_y = len(self.screenBuffer) - 1
        max_in_x = len(self.screenBuffer[0]) - 1
        for obj in self.objects:
            verts = obj.verts
            norms = obj.norms
            for (tri_num, tri), tri_norm in zip(enumerate(verts), norms):
                shading = -dot(self.lighting, tri_norm)

                if shading > 0.8:
                    char = chr(0x2593)
                elif shading > 0.4:
                    char = chr(0x2592)
                else:
                    char = chr(0x2591)

                y_verts = [vert[1] for vert in tri]
                x_verts = [vert[0] for vert in tri]
                y_min, y_max = math.floor(min(y_verts)), math.ceil(max(y_verts))
                x_min, x_max = math.floor(min(x_verts)), math.ceil(max(x_verts))

                y_range = y_max - y_min
                x_range = x_max - x_min

                for yi in range(y_range):
                    for xi in range(x_range):
                        x = x_min + xi
                        y = y_min + yi
                        if is_in_tri(tri, (x, y)):
                            px = x_min - self.min_scr_x + xi
                            py = y_min - self.min_scr_y + yi
                            if (0 <= px <= max_in_x) and (0 <= py <= max_in_y):
                                pixel_xy = self.screenBuffer[-py][px][0]

                                if pixel_xy == None:
                                    self.screenBuffer[-py][px] = (tri, char)
                                else:
                                    tri2 = pixel_xy
                                    max1 = max([vert[2] for vert in tri])
                                    min1 = min([vert[2] for vert in tri])
                                    max2 = max([vert[2] for vert in tri2])
                                    min2 = min([vert[2] for vert in tri2])

                                    if max1 < min2:
                                        pass
                                    elif max2 <= min1:
                                        self.screenBuffer[-py][px] = (tri, char)
                                    else:
                                        z1 = sum([b * pt[2] for (b, pt) in zip(cart_to_bary(tri, (x, y)), tri)])
                                        z2 = sum([b * pt[2] for (b, pt) in zip(cart_to_bary(tri2, (x, y)), tri2)])

                                        if z1 > z2:
                                            self.screenBuffer[-py][px] = (tri, char)

def read_stl(filename):
    with open(filename, 'rb') as file:
        file.read(80)  # Skip 80 byte file header
        tri_n = struct.unpack('<I', file.read(4))[0]  # Read number of triangles

        tri_verts = []  # Create list of triangle vertices
        tri_norms = []  # Create list of triangle normal vectors
        for i in range(tri_n):
            tri_norms.append(struct.unpack('<3f', file.read(12)))

            vert_pos = []
            for j in range(3):
                vert_pos.append(struct.unpack('<3f', file.read(12)))
            tri_verts.append(vert_pos)

            file.read(2)  # Skip 2 byte attribute for each triangle
    return tri_verts, tri_norms

def cart_to_bary(tri, pt):
    (x1, y1, _), (x2, y2, _), (x3, y3, _) = tri
    x, y = pt
    det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    bar1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    bar2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    bar3 = 1 - (bar1 + bar2)
    return bar1, bar2, bar3

def line_func(pt1, pt2, pt3):
    x1, y1, _ = pt1
    x2, y2, _ = pt2
    x3, y3 = pt3
    return (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3) > 0
    # z component of cross product of vector formed by pt1 and pt2 and vector formed by pt1 and pt3 to determine if the
    # angle is greater or less than 180 to determine if pt3 is on either side of the line formed by pt1 and pt2

def dot(vec1, vec2):
    product = 0
    for val1, val2 in zip(vec1, vec2):
        product += val1 * val2
    return product

def is_in_tri(tri, pt):
    pt1, pt2, pt3 = tri
    return line_func(pt1, pt2, pt) and line_func(pt2, pt3, pt) and line_func(pt3, pt1, pt)


light = [2 ** (1 / 2) / 2, 0, -2 ** (1 / 2) / 2]
char_ratio = 58 / 113


objects = []
for arg in sys.argv[1:]:
    if arg[0] == '-':
        pass # Optional command line args
    else:
        obj = Object3d.from_stl(arg)
        obj.center()
        obj.rot_x(-1)
        obj.scale(1, 1 * char_ratio, 1)
        obj.scale_to_fit(100, 100)
        obj.perspective(3*obj.z_max())
        objects.append(obj)

scene = Scene.create_trucated(objects, light)
scene.render()
scene.print()