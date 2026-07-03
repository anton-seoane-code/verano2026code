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
varying vec2 v_tex;
void main() {
    vec4 color = texture2D(u_texture, v_tex);
    if (color.a < 0.5) discard;
    float depth = gl_FragCoord.z / gl_FragCoord.w;
    float fog = clamp((depth - u_fog_near) / (u_fog_far - u_fog_near), 0.0, 1.0);
    gl_FragColor = mix(color, vec4(u_fog_color, 1.0), fog);
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
    img = Image.new('RGBA', (128, 64))
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
    }
    default_color = (200, 100, 200)
    for bid in range(8):
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
                    img.putpixel((px + dx, py + dy), (r, g, b, 255))
    mode = GL_RGBA
    tex_data = img.tobytes()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, mode, 128, 64, 0, mode, GL_UNSIGNED_BYTE, tex_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return tex_id

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.prog = make_program(VERTEX_SHADER, FRAGMENT_SHADER)
        self.tex_id = create_texture_atlas()
        self.vao = glGenVertexArrays(1)
        self.vbo_pos = glGenBuffers(1)
        self.vbo_tex = glGenBuffers(1)
        self.u_proj = glGetUniformLocation(self.prog, 'u_proj')
        self.u_view = glGetUniformLocation(self.prog, 'u_view')
        self.u_texture = glGetUniformLocation(self.prog, 'u_texture')
        self.u_fog_color = glGetUniformLocation(self.prog, 'u_fog_color')
        self.u_fog_near = glGetUniformLocation(self.prog, 'u_fog_near')
        self.u_fog_far = glGetUniformLocation(self.prog, 'u_fog_far')
        self.a_pos = glGetAttribLocation(self.prog, 'a_pos')
        self.a_tex = glGetAttribLocation(self.prog, 'a_tex')
        glUseProgram(self.prog)
        glUniform1i(self.u_texture, 0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.5, 0.7, 1.0, 1.0)

    def set_projection(self, fov, near, far):
        aspect = self.width / self.height
        proj = perspective_matrix(fov, aspect, near, far)
        glUniformMatrix4fv(self.u_proj, 1, GL_TRUE, proj)

    def set_view(self, pos, rotation):
        view = look_at_matrix(pos, rotation)
        glUniformMatrix4fv(self.u_view, 1, GL_TRUE, view)

    def render(self, chunks, pos):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniform3f(self.u_fog_color, 0.5, 0.7, 1.0)
        glUniform1f(self.u_fog_near, 40.0)
        glUniform1f(self.u_fog_far, 80.0)
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
