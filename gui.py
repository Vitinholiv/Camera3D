import pygame
import OpenGL.GL as gl
import OpenGL.GLU as glu
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

def process_window_resize(new_w, new_h):
    target_aspect = 16.0/9.0
    def_w = new_w
    def_h = int(new_w / target_aspect)
    
    if def_h > new_h:
        def_h = new_h
        def_w = int(new_h * target_aspect)
    
    delta_w = (new_w - def_w) // 2
    delta_h = (new_h - def_h) // 2
    
    pygame.display.set_mode((new_w, new_h), DOUBLEBUF | OPENGL | RESIZABLE)
    gl.glViewport(delta_w, delta_h, def_w, def_h)
    
    return def_w, def_h, delta_w, delta_h

def change_gl_mode(mode):
    if mode == 'PROJECTION':
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
    elif mode == 'MODELVIEW':
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

def _draw_rect(x, y, w, h, inset=1):
        ix = x + inset
        iy = y + inset
        iw = w - (2 * inset)
        ih = h - (2 * inset)
        
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(ix, iy)
        gl.glVertex2f(ix + iw, iy)
        gl.glVertex2f(ix + iw, iy + ih)
        gl.glVertex2f(ix, iy + ih)
        gl.glEnd()

def draw_ui_borders(current_w, current_h, delta_w, delta_h, A_w, A_h):
    gl.glViewport(0, 0, current_w, current_h)
    
    # Save State
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    glu.gluOrtho2D(0, current_w, 0, current_h)
    
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)

    # Drawing
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glLineWidth(1.0)
    
    box_left_w = int(5 * A_w)
    box_right_w = int(11 * A_w)
    box_full_h = int(9 * A_h)
    box_half_h = int(4.5 * A_h)
    
    x_base = delta_w
    y_base = delta_h

    _draw_rect(x_base, y_base, box_left_w, box_full_h)
    _draw_rect(x_base + box_left_w, y_base, box_right_w, box_half_h)
    _draw_rect(x_base + box_left_w, y_base + box_half_h, box_right_w, box_half_h)

    # Restore State
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()