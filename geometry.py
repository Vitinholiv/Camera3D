import numpy as np
from OpenGL.GL import (
    GL_LIGHTING, GL_POINTS, GL_LINES, GL_QUADS, GL_BLEND,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    glEnable, glDisable, glPointSize, glLineWidth, glEnd, glBegin,
    glVertex3f, glVertex3fv, glColor3f, glColor4f,
    glBlendFunc, glDepthMask
)

PROJECTION_CENTER_COLOR = (1.0, 1.0, 0.0)
OPTICAL_AXIS_COLOR      = (1.0, 0.5, 0.1)
FRUSTUM_COLOR           = (0.3, 1.0, 0.6)
UP_VECTOR_COLOR         = (0.0, 1.0, 1.0)

FACE_COLORS = {
    "near":   (0.2, 0.8, 1.0, 0.45),
    "far":    (0.2, 0.8, 1.0, 0.45),
    "left":   (0.2, 0.8, 1.0, 0.45),
    "right":  (0.2, 0.8, 1.0, 0.45),
    "top":    (0.2, 0.8, 1.0, 0.45),
    "bottom": (0.2, 0.8, 1.0, 0.45),
}

def get_frustum_corners(camera):
    p = camera.params
    u, v, n_vec = camera.get_orthonormal_base()
    C = np.array(p.C, dtype=float)

    scale_near = p.n / p.d
    scale_far  = p.f / p.d

    center_near = C + n_vec * p.n
    center_far  = C + n_vec * p.f

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

    near_corners = get_plane_corners(center_near, scale_near)
    far_corners  = get_plane_corners(center_far,  scale_far)
    return near_corners, far_corners

def get_frustum_planes(camera):
    p = camera.params
    _, __, n_vec = camera.get_orthonormal_base()
    C  = np.array(p.C, dtype=float)
    nc, _ = get_frustum_corners(camera)

    def make_plane(normal, point_on_plane):
        n = normal / np.linalg.norm(normal)
        return [float(n[0]), float(n[1]), float(n[2]),
                float(-np.dot(n, point_on_plane))]

    return [
        make_plane( n_vec,                           C + n_vec * p.n),  # near
        make_plane(-n_vec,                           C + n_vec * p.f),  # far
        make_plane(np.cross(nc[3]-C, nc[0]-C), C),  # left
        make_plane(np.cross(nc[1]-C, nc[2]-C), C),  # right
        make_plane(np.cross(nc[0]-C, nc[1]-C), C),  # top
        make_plane(np.cross(nc[2]-C, nc[3]-C), C),  # bottom
    ]

def _draw_frustum_edges(near_corners, far_corners):
    r, g, b = FRUSTUM_COLOR
    glColor3f(r, g, b)
    glBegin(GL_LINES)

    for i in range(4):
        glVertex3fv(near_corners[i])
        glVertex3fv(far_corners[i])

    for i in range(4):
        glVertex3fv(near_corners[i])
        glVertex3fv(near_corners[(i + 1) % 4])

    for i in range(4):
        glVertex3fv(far_corners[i])
        glVertex3fv(far_corners[(i + 1) % 4])

    glEnd()


def _draw_frustum_faces(near_corners, far_corners):
    nc = near_corners
    fc = far_corners

    faces = [
        ("near",   [nc[0], nc[1], nc[2], nc[3]]),
        ("far",    [fc[3], fc[2], fc[1], fc[0]]),
        ("left",   [fc[0], fc[3], nc[3], nc[0]]),
        ("right",  [nc[1], nc[2], fc[2], fc[1]]),
        ("top",    [fc[0], fc[1], nc[1], nc[0]]),
        ("bottom", [nc[3], nc[2], fc[2], fc[3]]),
    ]

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(False)

    glBegin(GL_QUADS)
    for name, verts in faces:
        r, g, b, a = FACE_COLORS[name]
        glColor4f(r, g, b, a)
        for v in verts:
            glVertex3fv(v)
    glEnd()

    glDepthMask(True)
    glDisable(GL_BLEND)

    glLineWidth(1.2)
    _draw_frustum_edges(near_corners, far_corners)
    glLineWidth(1.0)


def draw_virtual_camera(camera, frustum_mode="EDGES"):
    p = camera.params
    C = np.array(p.C, dtype=float)
    near_corners, far_corners = get_frustum_corners(camera)

    glDisable(GL_LIGHTING)

    # Projection Center
    glPointSize(8.0)
    r, g, b = PROJECTION_CENTER_COLOR
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    glVertex3fv(C)
    glEnd()

    # Frustum
    if frustum_mode == "FACES":
        _draw_frustum_faces(near_corners, far_corners)
    else:
        _draw_frustum_edges(near_corners, far_corners)

    # Optical Axis
    u, v, n_vec = camera.get_orthonormal_base()
    optical_axis_end = C + n_vec * p.f
    r, g, b = OPTICAL_AXIS_COLOR
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex3fv(C)
    glVertex3fv(optical_axis_end)
    glEnd()

    # Up Vector
    up_end = C + v * (p.n * 0.8)
    r, g, b = UP_VECTOR_COLOR
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex3fv(C)
    glVertex3fv(up_end)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_origin_axes():
    glDisable(GL_LIGHTING)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0); glVertex3f(0, 0, 0); glVertex3f(50, 0, 0)
    glColor3f(0.0, 1.0, 0.0); glVertex3f(0, 0, 0); glVertex3f(0, 50, 0)
    glColor3f(0.0, 0.0, 1.0); glVertex3f(0, 0, 0); glVertex3f(0, 0, 50)
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)


def draw_xz_grid(size=10, step=1):
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(-size, -0.1, i);  glVertex3f(size, -0.1, i)
        glVertex3f(i, -0.1, -size);  glVertex3f(i, -0.1, size)
    glEnd()
    glEnable(GL_LIGHTING)
