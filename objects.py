import OpenGL.GL as gl
import OpenGL.GLU as glu

class SceneObject:
    def __init__(self, position=[0, 0, 0], color=(1, 1, 1)):
        self.position = position
        self.color = color

    def draw(self):
        pass

class Sphere(SceneObject):
    def __init__(self, position=[0, 0, 0], radius=1.0, color=(1, 1, 1), detail=32):
        super().__init__(position, color)
        self.radius = radius
        self.detail = detail
        self.quadric = glu.gluNewQuadric()

    def draw(self, color_mult=1.0):
        gl.glPushMatrix()
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])
        r, g, b = (c * color_mult for c in self.color)
        gl.glColor3f(r, g, b)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, (r, g, b, 1.0))
        glu.gluSphere(self.quadric, self.radius, self.detail, self.detail)
        gl.glPopMatrix()