import numpy as np
from OpenGL.GL import GL_LIGHTING, GL_POINTS, GL_LINES
from OpenGL.GL import glEnable, glDisable, glPointSize, glEnd, glBegin
from OpenGL.GL import glVertex3f, glVertex3fv, glColor3f

PROJECTION_CENTER_COLOR = (1.0, 1.0, 0.0)
OPTICAL_AXIS_COLOR = (1.0, 0.5, 0.1)
FRUSTUM_COLOR = (0.3, 1.0, 0.6)
UP_VECTOR_COLOR = (0.0, 1.0, 1.0)

def get_frustum_corners(camera):
    p = camera.params
    u, v, n_vec = camera.get_orthonormal_base()
    C = np.array(p.C, dtype=float)
    
    # Scale factors
    scale_near = p.n / p.d
    scale_far = p.f / p.d
    
    # Centers
    center_near = C + n_vec * p.n
    center_far = C + n_vec * p.f

    def get_plane_corners(center, scale):
        u_min_s = p.u_min * scale
        u_max_s = p.u_max * scale
        v_min_s = p.v_min * scale
        v_max_s = p.v_max * scale

        top_left     = center + u_min_s * u + v_max_s * v
        top_right    = center + u_max_s * u + v_max_s * v
        bottom_left  = center + u_min_s * u + v_min_s * v
        bottom_right = center + u_max_s * u + v_min_s * v

        return [top_left, top_right, bottom_right, bottom_left]
        
    # Corners
    near_corners = get_plane_corners(center_near, scale_near)
    far_corners = get_plane_corners(center_far, scale_far)
    
    return near_corners, far_corners

def draw_virtual_camera(camera):
    p = camera.params
    C = np.array(p.C, dtype=float)
    near_corners, far_corners = get_frustum_corners(camera)

    glDisable(GL_LIGHTING)
    
    # Draw Projection Center

    glPointSize(8.0)
    c1, c2, c3 = PROJECTION_CENTER_COLOR
    glColor3f(c1,c2,c3)
    glBegin(GL_POINTS)
    glVertex3fv(C)
    glEnd()
    
    # Draw Frustum

    c1, c2, c3 = FRUSTUM_COLOR
    glColor3f(c1,c2,c3)
    glBegin(GL_LINES)
    # Distance Edges
    for corner in far_corners:
        glVertex3fv(C)
        glVertex3fv(corner)
    # Near Plane Sides
    for i in range(4):
        glVertex3fv(near_corners[i])
        glVertex3fv(near_corners[(i+1)%4])
    # Far Plane Sides
    for i in range(4):
        glVertex3fv(far_corners[i])
        glVertex3fv(far_corners[(i+1)%4])
    glEnd()
    
    # Draw Optical Axis

    u, v, n_vec = camera.get_orthonormal_base()
    optical_axis_end = C + n_vec * p.f
    c1, c2, c3 = OPTICAL_AXIS_COLOR
    glColor3f(c1,c2,c3)
    glBegin(GL_LINES)
    glVertex3fv(C)
    glVertex3fv(optical_axis_end)
    glEnd()
    
    # Draw Up Vector

    up_end = C + v * (p.n * 0.8) 
    c1, c2, c3 = UP_VECTOR_COLOR
    glColor3f(c1,c2,c3)
    glBegin(GL_LINES)
    glVertex3fv(C)
    glVertex3fv(up_end)
    glEnd()

    glEnable(GL_LIGHTING)

def draw_origin_axes():
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(5.0, 0.0, 0.0)
    glColor3f(0.0, 1.0, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 5.0, 0.0)
    glColor3f(0.0, 0.0, 1.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, 5.0)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_xz_grid(size=10, step=1):
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(-size, 0, i)
        glVertex3f(size, 0, i)
        glVertex3f(i, 0, -size)
        glVertex3f(i, 0, size)
    glEnd()
    glEnable(GL_LIGHTING)