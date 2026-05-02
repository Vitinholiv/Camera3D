import math
import pygame
import numpy as np
import OpenGL.GLU as glu

class VirtualCamera:
    def __init__(self, parameters):
        self.params = parameters
        self.active = False
        self.yaw = -90.0
        self.pitch = 0.0
        self.speeds = [0.05, 0.2, 0.6]
        self.speed_idx = 1
        self.mouse_sensitivity = 0.1

    def toggle_speed(self):
        self.speed_idx = (self.speed_idx + 1) % len(self.speeds)

    def rotate(self, rel_x, rel_y):
        if not self.active: return
        self.yaw += rel_x * self.mouse_sensitivity
        self.pitch -= rel_y * self.mouse_sensitivity
        self.pitch = max(-89, min(89, self.pitch))
        
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        
        new_n = [
            math.cos(rad_yaw) * math.cos(rad_pitch),
            math.sin(rad_pitch),
            math.sin(rad_yaw) * math.cos(rad_pitch)
        ]
        self.params.N = new_n

    def move(self, keys):
        if not self.active: return
        s = self.speeds[self.speed_idx]

        rad_yaw = math.radians(self.yaw)
        forward = np.array([math.cos(rad_yaw), 0, math.sin(rad_yaw)])
        right = np.array([-math.sin(rad_yaw), 0, math.cos(rad_yaw)])
        up = np.array([0,1,0])
        
        pos = np.array(self.params.C, dtype=float)
        if keys[pygame.K_w]: pos += forward * s
        if keys[pygame.K_s]: pos -= forward * s
        if keys[pygame.K_a]: pos -= right * s
        if keys[pygame.K_d]: pos += right * s
        if keys[pygame.K_e]: pos += up * s
        if keys[pygame.K_q]: pos -= up * s
        
        self.params.C = pos.tolist()

    def get_orthonormal_base(self):
        N = np.array(self.params.N, dtype=float)
        n = N / np.linalg.norm(N)
        V = np.array(self.params.V, dtype=float)
        v_unnorm = V - np.dot(V, n) * n
        v = v_unnorm / np.linalg.norm(v_unnorm)
        u = np.cross(n, v)
        return u, v, n

    def get_view_matrix(self):
        u, v, n = self.get_orthonormal_base()
        C = np.array(self.params.C, dtype=float)
        
        # Translation Matrix
        T_cam = np.eye(4)
        T_cam[0, 3] = -C[0]
        T_cam[1, 3] = -C[1]
        T_cam[2, 3] = -C[2]
        
        # Rotation Matrix
        R_cam = np.eye(4)
        R_cam[0, :3] = u
        R_cam[1, :3] = v
        R_cam[2, :3] = n

        return R_cam @ T_cam

    def get_normalization_matrices(self):
        p = self.params

        I_u = (p.u_min + p.u_max) / 2.0
        I_v = (p.v_min + p.v_max) / 2.0
        s_u = (p.u_max - p.u_min) / 2.0
        s_v = (p.v_max - p.v_min) / 2.0

        M1 = np.array([
            [1, 0, -I_u / p.d, 0],
            [0, 1, -I_v / p.d, 0],
            [0, 0, 1,          0],
            [0, 0, 0,          1]
        ], dtype=float)

        M2 = np.array([
            [p.d / (s_u * p.f), 0,                 0,     0],
            [0,                 p.d / (s_v * p.f), 0,     0],
            [0,                 0,                 1/p.f, 0],
            [0,                 0,                 0,     1]
        ], dtype=float)

        a_z = (p.f + p.n) / (p.f - p.n)
        b_z = -2.0 * p.n  / (p.f - p.n)

        T_proj = np.array([
            [1, 0, 0,   0  ],
            [0, 1, 0,   0  ],
            [0, 0, a_z, b_z],
            [0, 0, 1,   0  ]
        ], dtype=float)

        return M1, M2, T_proj

    def get_full_projection_matrix(self):
        M1, M2, T_proj = self.get_normalization_matrices()
        return T_proj @ (M2 @ M1)

class Observer:
    def __init__(self):
        self.pos = np.array([10.0, 8.0, 10.0])
        self.yaw = -135.0
        self.pitch = -30.0
        
        self.speeds = [0.05, 0.2, 0.6]
        self.speed_idx = 1
        self.active = False
        self.mouse_sensitivity = 0.1

    def toggle_speed(self):
        self.speed_idx = (self.speed_idx + 1) % len(self.speeds)

    def update_view(self):
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        
        front = np.array([
            math.cos(rad_yaw) * math.cos(rad_pitch),
            math.sin(rad_pitch),
            math.sin(rad_yaw) * math.cos(rad_pitch)
        ])
        
        target = self.pos + front
        glu.gluLookAt(self.pos[0], self.pos[1], self.pos[2],
                      target[0], target[1], target[2],
                      0, 1, 0)

    def move(self, keys):
        if not self.active: return
        
        s = self.speeds[self.speed_idx]
        rad_yaw = math.radians(self.yaw)
        forward = np.array([math.cos(rad_yaw), 0, math.sin(rad_yaw)])
        right = np.array([-math.sin(rad_yaw), 0, math.cos(rad_yaw)])
        up = np.array([0, 1, 0])
        
        if keys[pygame.K_w]: self.pos += forward * s
        if keys[pygame.K_s]: self.pos -= forward * s
        if keys[pygame.K_a]: self.pos -= right * s
        if keys[pygame.K_d]: self.pos += right * s
        if keys[pygame.K_e]: self.pos += up * s
        if keys[pygame.K_q]: self.pos -= up * s

    def rotate(self, rel_x, rel_y):
        if not self.active: return
        self.yaw += rel_x * self.mouse_sensitivity
        self.pitch -= rel_y * self.mouse_sensitivity
        self.pitch = max(-89, min(89, self.pitch))