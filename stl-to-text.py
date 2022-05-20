#!/usr/bin/env python3

import math
import struct
import sys
import os
from typing import List


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

        fac = x_fac if x_fac < y_fac else y_fac
        self.scale(fac, fac, fac)
    
    def orign(self):
        self.translate(-self.x_min(), -self.y_min(), -self.z_min())

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

def scale_to_fit(objects: List[Object3d], x_size: int, y_size: int):
    max_scr_x = math.ceil(max([obj.x_max() for obj in objects]))
    min_scr_x = math.floor(min([obj.x_min() for obj in objects]))
    max_scr_y = math.ceil(max([obj.y_max() for obj in objects]))
    min_scr_y = math.floor(min([obj.y_min() for obj in objects]))

    x_fac = x_size / (max_scr_x - min_scr_x)
    y_fac = y_size / (max_scr_y - min_scr_y)
    
    fac = x_fac if x_fac < y_fac else y_fac
    [obj.scale(fac, fac, fac) for obj in objects]

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

if __name__ == "__main__":
    try:
        (x_term, y_term) = os.get_terminal_size()
    except OSError:
        print("Failed to get terminal size. Defaulting to 100x100", file=sys.stderr)
        x_term = 100
        y_term = 100

    light = [2 ** (1 / 2) / 2, 0, -2 ** (1 / 2) / 2]
    char_ratio = 58 / 113
    help = """\
Usage: stl-to-text [OPTIONS]... [FILE [OPTIONS]...]...
Display mesh encoded by binary stl FILE transformed by OPTIONS
transformations are done in the order OPTIONS is listed
Example: stl-to-text foo.stl -x=50 bar.stl -ry=2

Transforms:
  -x=, -y=, -z=           translates the preceding object by the 
                          amount of cells that follows the equals sign
  -s=, -sx=, -sy=, -sz=   scales the preceding object by the amount that 
                          follows the equals sign; -s scales all axises 
                          equally
  -rx=, -ry=, -rz=        rotates the preceding object by the amount of 
                          radians that follows the equals sign"""

    objects = []
    last_object = None
    if len(sys.argv) == 1:
        print(help)
        quit(0)
    if sys.argv[1][0] == '-':
        print("stl-to-text: a file must be entered before any options", file=sys.stderr)
        quit(1)
    for arg in sys.argv[1:]:
        if arg[0] != '-':
            try:
                obj = Object3d.from_stl(arg)
            except IOError as err:
                print("stl-to-text: can't open file:", err, file=sys.stderr)
                quit(1)

            obj.center()
            obj.scale_to_fit(x_term, y_term)
            objects.append(obj)
            last_object = obj             
        else:
            if arg == "--help":
                    print(help)
                    quit(0)
            try:
                if arg[:3] == "-x=":
                    last_object.translate(xt=float(arg[3:]))
                elif arg[:3] == "-y=":
                    last_object.translate(yt=float(arg[3:]))
                elif arg[:3] == "-z=":
                    last_object.translate(zt=float(arg[3:]))
                
                elif arg[:4] == "-rx=":
                    last_object.rot_x(float(arg[4:]))
                elif arg[:4] == "-ry=":
                    last_object.rot_y(float(arg[4:]))
                elif arg[:4] == "-rz=":
                    last_object.rot_z(float(arg[4:]))
                
                elif arg[:3] == "-s=":
                    fac = float(arg[3:])
                    last_object.scale(fac, fac, fac)
                elif arg[:4] == "-sx=":
                    last_object.scale(sx=float(arg[4:]))
                elif arg[:4] == "-sy=":
                    last_object.scale(sy=float(arg[4:]))
                elif arg[:4] == "-sz=":
                    last_object.scale(sz=float(arg[4:]))
                
                else:
                    print("stl-to-text: flag not recognized", file=sys.stderr)
                    quit(1)

            except ValueError as err:
                print("stl-to-text: a valid float must by passed to flags:", err, file=sys.stderr)
                quit(1)

    
    closest = max([obj.z_max() for obj in objects])
    for obj in objects:
        obj.scale(1, 1 * char_ratio, 1)
        obj.perspective(3*closest)

    scale_to_fit(objects, x_term-1, y_term)
    scene = Scene.create_trucated(objects, light)
    scene.render()
    scene.print()