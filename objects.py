import OpenGL.GL as gl
import OpenGL.GLU as glu
import os

class SceneObject:
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], color=(1, 1, 1)):
        self.position = position
        self.rotation = rotation
        self.color = color

    def draw(self):
        pass

class Sphere(SceneObject):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], radius=1.0, color=(1, 1, 1), detail=32):
        super().__init__(position, rotation, color)
        self.radius = radius
        self.detail = detail
        self.quadric = glu.gluNewQuadric()

    def draw(self, color_mult=1.0):
        gl.glPushMatrix()
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])
        
        if self.rotation[0] != 0: gl.glRotatef(self.rotation[0], 1, 0, 0)
        if self.rotation[1] != 0: gl.glRotatef(self.rotation[1], 0, 1, 0)
        if self.rotation[2] != 0: gl.glRotatef(self.rotation[2], 0, 0, 1)

        r, g, b = (c * color_mult for c in self.color)
        gl.glColor3f(r, g, b)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, (r, g, b, 1.0))
        glu.gluSphere(self.quadric, self.radius, self.detail, self.detail)
        
        gl.glPopMatrix()

class MeshObject(SceneObject):
    def __init__(self, filename, position=[0, 0, 0], rotation=[0, 0, 0], color=(1, 1, 1), scale=1.0):
        super().__init__(position, rotation, color)
        self.filename = os.path.join('objs', filename)
        self.scale = scale
        self.vertices = []
        self.normals = []
        self.faces = []
        self.display_list = None 
        self._load_obj()

    def _load_obj(self):
        if not os.path.exists(self.filename):
            print(f"Arquivo não encontrado: {self.filename}")
            return

        with open(self.filename, 'r') as file:
            for line in file:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                
                if values[0] == 'v':
                    v = [float(x) * self.scale for x in values[1:4]]
                    self.vertices.append(v)
                    
                elif values[0] == 'vn':
                    n = [float(x) for x in values[1:4]]
                    self.normals.append(n)
                    
                elif values[0] == 'f':
                    face = []
                    for v in values[1:]:
                        w = v.split('/')
                        v_idx = int(w[0]) - 1
                        n_idx = int(w[2]) - 1 if len(w) >= 3 and w[2] else -1
                        face.append((v_idx, n_idx))
                    self.faces.append(face)

    def _compile_display_list(self):
        if not self.vertices or not self.faces:
            return

        self.display_list = gl.glGenLists(1)
        gl.glNewList(self.display_list, gl.GL_COMPILE)
        
        for face in self.faces:
            if len(face) == 3: gl.glBegin(gl.GL_TRIANGLES)
            elif len(face) == 4: gl.glBegin(gl.GL_QUADS)
            else: gl.glBegin(gl.GL_POLYGON)
                
            for v_idx, n_idx in face:
                if n_idx != -1 and n_idx < len(self.normals):
                    gl.glNormal3fv(self.normals[n_idx])
                gl.glVertex3fv(self.vertices[v_idx])
                
            gl.glEnd()
        gl.glEndList()

    def draw(self, color_mult=1.0):
        if self.display_list is None:
            self._compile_display_list()
            
        if self.display_list is None:
            return

        gl.glPushMatrix()
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])

        if self.rotation[0] != 0: gl.glRotatef(self.rotation[0], 1, 0, 0)
        if self.rotation[1] != 0: gl.glRotatef(self.rotation[1], 0, 1, 0)
        if self.rotation[2] != 0: gl.glRotatef(self.rotation[2], 0, 0, 1)
        
        r, g, b = (c * color_mult for c in self.color)
        gl.glColor3f(r, g, b)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, (r, g, b, 1.0))
        gl.glCallList(self.display_list)
        gl.glPopMatrix()

world_objects = [
    Sphere(position=[5, 2, 5], radius=2.0, color=(1.0, 0.5, 0.5)),
    MeshObject(filename="tree.obj", position=[30, 0, 30], scale=0.6, color=(0.5, 1.0, 0.5)),
    MeshObject(filename="horse.obj", position=[0, 0, 30], rotation=[-90, 0, 90], scale=0.0025, color=(0.35, 0.25, 0.2)),
    MeshObject(filename="plane.obj", position=[0, 40, 0], rotation=[-90, 0, 90], scale=1.5, color=(0.9, 0.25, 0.5)),
    MeshObject(filename="rj.obj", position=[45, 0, 0], rotation=[-90, 0, 0], scale=0.01, color=(0.0420, 0.24, 0.67)),
]