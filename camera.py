import numpy as np

class VirtualCamera:
    def __init__(self, parameters):
        self.params = parameters

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
        
        z0 = p.n / p.f
        T_proj = np.array([
            [1, 0, 0,            0],
            [0, 1, 0,            0],
            [0, 0, 1/(1-z0),    -z0/(1-z0)],
            [0, 0, 1,            0]
        ], dtype=float)
        
        return M1, M2, T_proj

    def get_full_projection_matrix(self):
        M1, M2, T_proj = self.get_normalization_matrices()
        return T_proj @ (M2 @ M1)