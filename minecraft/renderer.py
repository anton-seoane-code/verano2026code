import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image

VERTEX_SHADER = """
#version 120
attribute vec3 a_pos;
attribute vec2 a_tex;
uniform mat4 u_proj;
uniform mat4 u_view;
varying vec2 v_tex;
void main() {
    gl_Position = u_proj * u_view * vec4(a_pos, 1.0);
    v_tex = a_tex;
}
"""

FRAGMENT_SHADER = """
#version 120
uniform sampler2D u_texture;
uniform vec3 u_fog_color;
uniform float u_fog_near;
uniform float u_fog_far;
uniform float u_sky_top;
varying vec2 v_tex;
void main() {
    vec4 color = texture2D(u_texture, v_tex);
    if (color.a < 0.5) discard;
    float depth = gl_FragCoord.z / gl_FragCoord.w;
    float fog = clamp((depth - u_fog_near) / (u_fog_far - u_fog_near), 0.0, 1.0);
    gl_FragColor = mix(color, vec4(u_fog_color, 1.0), fog);
}
"""

HIGHLIGHT_VS = """
#version 120
attribute vec3 a_pos;
uniform mat4 u_proj;
uniform mat4 u_view;
void main() {
    gl_Position = u_proj * u_view * vec4(a_pos, 1.0);
}
"""

HIGHLIGHT_FS = """
#version 120
uniform vec4 u_color;
void main() {
    gl_FragColor = u_color;
}
"""

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader

def make_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(prog).decode())
    return prog

def create_texture_atlas():
    img = Image.new('RGBA', (256, 64))
    colors = {
        (1, 'top'): (90, 180, 60),
        (1, 'side'): (110, 150, 50),
        (2, 'top'): (130, 90, 50),
        (3, 'top'): (120, 120, 120),
        (4, 'top'): (100, 70, 40),
        (4, 'side'): (80, 55, 30),
        (5, 'top'): (180, 160, 100),
        (6, 'top'): (210, 190, 140),
        (7, 'top'): (160, 80, 70),
        (8, 'top'): (50, 140, 50),
    }
    default_color = (200, 100, 200)
    for bid in range(16):
        for variant in ['top', 'side', 'bottom']:
            key = (bid, variant)
            color = colors.get(key, default_color)
            px = bid * 16
            py = {'top': 0, 'side': 16, 'bottom': 32}[variant]
            for dx in range(16):
                for dy in range(16):
                    r, g, b = color
                    r = max(0, min(255, r + int((dx - 8) * 2)))
                    g = max(0, min(255, g + int((dy - 8) * 2)))
                    b = max(0, min(255, b + int((dx - dy) * 1.5)))
                    alpha = 255
                    if bid == 8:
                        noise = (dx * 7 + dy * 31 + bid * 13) % 4
                        if noise == 0:
                            alpha = 0
                    img.putpixel((px + dx, py + dy), (r, g, b, alpha))
    mode = GL_RGBA
    tex_data = img.tobytes()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, mode, 256, 64, 0, mode, GL_UNSIGNED_BYTE, tex_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return tex_id

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.prog = make_program(VERTEX_SHADER, FRAGMENT_SHADER)
        self.tex_id = create_texture_atlas()

        hl_prog = make_program(HIGHLIGHT_VS, HIGHLIGHT_FS)
        self.hl_prog = hl_prog
        self.hl_u_proj = glGetUniformLocation(hl_prog, 'u_proj')
        self.hl_u_view = glGetUniformLocation(hl_prog, 'u_view')
        self.hl_u_color = glGetUniformLocation(hl_prog, 'u_color')
        self.hl_a_pos = glGetAttribLocation(hl_prog, 'a_pos')

        self.vao = glGenVertexArrays(1)
        self.vbo_pos = glGenBuffers(1)
        self.vbo_tex = glGenBuffers(1)
        self.u_proj = glGetUniformLocation(self.prog, 'u_proj')
        self.u_view = glGetUniformLocation(self.prog, 'u_view')
        self.u_texture = glGetUniformLocation(self.prog, 'u_texture')
        self.u_fog_color = glGetUniformLocation(self.prog, 'u_fog_color')
        self.u_fog_near = glGetUniformLocation(self.prog, 'u_fog_near')
        self.u_fog_far = glGetUniformLocation(self.prog, 'u_fog_far')
        self.u_sky_top = glGetUniformLocation(self.prog, 'u_sky_top')
        self.a_pos = glGetAttribLocation(self.prog, 'a_pos')
        self.a_tex = glGetAttribLocation(self.prog, 'a_tex')
        glUseProgram(self.prog)
        glUniform1i(self.u_texture, 0)

        self._sky_angle = 0.0
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def set_projection(self, fov, near, far):
        aspect = self.width / self.height
        proj = perspective_matrix(fov, aspect, near, far)
        glUniformMatrix4fv(self.u_proj, 1, GL_TRUE, proj)
        self._proj = proj

    def set_view(self, pos, rotation):
        view = look_at_matrix(pos, rotation)
        glUniformMatrix4fv(self.u_view, 1, GL_TRUE, view)
        self._view = view

    def render(self, chunks, pos, highlight=None):
        self._sky_angle = (self._sky_angle + 0.002) % (2 * np.pi)
        sky_h = 0.55 + 0.15 * np.sin(self._sky_angle)
        sky_r = max(0.0, 0.4 + 0.15 * np.sin(self._sky_angle))
        sky_g = max(0.0, 0.6 + 0.1 * np.sin(self._sky_angle + 1))
        sky_b = 0.8 + 0.15 * np.sin(self._sky_angle + 2)
        glClearColor(sky_r, sky_g, sky_b, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.prog)
        glUniform3f(self.u_fog_color, sky_r, sky_g, sky_b)
        glUniform1f(self.u_fog_near, 40.0)
        glUniform1f(self.u_fog_far, 80.0)
        glUniformMatrix4fv(self.u_proj, 1, GL_TRUE, self._proj)
        glUniformMatrix4fv(self.u_view, 1, GL_TRUE, self._view)
        glUniform1f(self.u_sky_top, sky_h)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glBindVertexArray(self.vao)
        glEnableVertexAttribArray(self.a_pos)
        glEnableVertexAttribArray(self.a_tex)
        for c, (verts, tex) in chunks:
            n = len(verts) // 3
            if n == 0:
                continue
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_pos)
            glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(self.a_pos, 3, GL_FLOAT, GL_FALSE, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_tex)
            glBufferData(GL_ARRAY_BUFFER, tex.nbytes, tex, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(self.a_tex, 2, GL_FLOAT, GL_FALSE, 0, None)
            glDrawArrays(GL_TRIANGLES, 0, n)
        glDisableVertexAttribArray(self.a_pos)
        glDisableVertexAttribArray(self.a_tex)

        if highlight:
            bx, by, bz = highlight
            self._draw_highlight(bx, by, bz)

    def _draw_highlight(self, bx, by, bz):
        hw = 0.501
        verts = np.array([
            [-hw, -hw, -hw], [hw, -hw, -hw], [hw, -hw, -hw], [hw, -hw, hw],
            [hw, -hw, hw], [-hw, -hw, hw], [-hw, -hw, hw], [-hw, -hw, -hw],
            [-hw, hw, -hw], [hw, hw, -hw], [hw, hw, -hw], [hw, hw, hw],
            [hw, hw, hw], [-hw, hw, hw], [-hw, hw, hw], [-hw, hw, -hw],
            [-hw, -hw, -hw], [-hw, hw, -hw], [hw, -hw, -hw], [hw, hw, -hw],
            [hw, -hw, hw], [hw, hw, hw], [-hw, -hw, hw], [-hw, hw, hw],
        ], dtype=np.float32)
        verts[:, 0] += bx + 0.5
        verts[:, 1] += by + 0.5
        verts[:, 2] += bz + 0.5
        glUseProgram(self.hl_prog)
        glUniformMatrix4fv(self.hl_u_proj, 1, GL_TRUE, self._proj)
        glUniformMatrix4fv(self.hl_u_view, 1, GL_TRUE, self._view)
        glUniform4f(self.hl_u_color, 1.0, 1.0, 1.0, 0.6)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self.vao)
        glEnableVertexAttribArray(self.hl_a_pos)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(self.hl_a_pos, 3, GL_FLOAT, GL_FALSE, 0, None)
        glDrawArrays(GL_LINES, 0, 24)
        glDisableVertexAttribArray(self.hl_a_pos)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glUseProgram(self.prog)

def perspective_matrix(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
        [0, 0, -1, 0],
    ], dtype=np.float32)

def look_at_matrix(pos, rotation):
    yaw, pitch = rotation
    forward = np.array([np.sin(yaw) * np.cos(pitch), np.sin(pitch), np.cos(yaw) * np.cos(pitch)])
    forward = forward / np.linalg.norm(forward)
    world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(forward, world_up)
    right = right / np.linalg.norm(right)
    up = np.cross(right, forward)
    rx, ry, rz = right
    ux, uy, uz = up
    fx, fy, fz = forward
    view = np.array([
        [rx, ry, rz, -np.dot(right, pos)],
        [ux, uy, uz, -np.dot(up, pos)],
        [-fx, -fy, -fz, np.dot(forward, pos)],
        [0, 0, 0, 1],
    ], dtype=np.float32)
    return view
