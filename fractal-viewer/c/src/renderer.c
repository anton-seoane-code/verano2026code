#include "renderer.h"
#include <SDL2/SDL_opengl.h>
#include <stdlib.h>
#include <stdio.h>

static const char *vert_src =
    "#version 330 core\n"
    "layout(location = 0) in vec2 pos;\n"
    "layout(location = 1) in vec2 tex;\n"
    "out vec2 uv;\n"
    "void main() {\n"
    "    gl_Position = vec4(pos, 0.0, 1.0);\n"
    "    uv = tex;\n"
    "}\n";

static const char *frag_src =
    "#version 330 core\n"
    "in vec2 uv;\n"
    "out vec4 color;\n"
    "uniform sampler2D tex_sampler;\n"
    "void main() {\n"
    "    color = texture(tex_sampler, uv);\n"
    "}\n";

static unsigned int compile_shader(unsigned int type, const char *src) {
    unsigned int shader = glCreateShader(type);
    glShaderSource(shader, 1, &src, NULL);
    glCompileShader(shader);
    int success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char log[512];
        glGetShaderInfoLog(shader, 512, NULL, log);
        fprintf(stderr, "Shader compile error: %s\n", log);
        return 0;
    }
    return shader;
}

static unsigned int link_program(unsigned int vs, unsigned int fs) {
    unsigned int prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, fs);
    glLinkProgram(prog);
    int success;
    glGetProgramiv(prog, GL_LINK_STATUS, &success);
    if (!success) {
        char log[512];
        glGetProgramInfoLog(prog, 512, NULL, log);
        fprintf(stderr, "Program link error: %s\n", log);
        return 0;
    }
    return prog;
}

int renderer_init(Renderer *ren, int width, int height) {
    ren->width = width;
    ren->height = height;

    unsigned int vs = compile_shader(GL_VERTEX_SHADER, vert_src);
    unsigned int fs = compile_shader(GL_FRAGMENT_SHADER, frag_src);
    if (!vs || !fs) return 0;
    ren->shader = link_program(vs, fs);
    glDeleteShader(vs);
    glDeleteShader(fs);
    if (!ren->shader) return 0;

    float verts[] = {
        -1.0f, -1.0f,  0.0f, 0.0f,
         1.0f, -1.0f,  1.0f, 0.0f,
        -1.0f,  1.0f,  0.0f, 1.0f,
         1.0f,  1.0f,  1.0f, 1.0f,
    };
    glGenVertexArrays(1, &ren->vao);
    glGenBuffers(1, &ren->vbo);
    glBindVertexArray(ren->vao);
    glBindBuffer(GL_ARRAY_BUFFER, ren->vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(verts), verts, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));

    glGenTextures(1, &ren->tex_id);
    glBindTexture(GL_TEXTURE_2D, ren->tex_id);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);

    glUseProgram(ren->shader);
    glUniform1i(glGetUniformLocation(ren->shader, "tex_sampler"), 0);

    return 1;
}

void renderer_destroy(Renderer *ren) {
    glDeleteTextures(1, &ren->tex_id);
    glDeleteVertexArrays(1, &ren->vao);
    glDeleteBuffers(1, &ren->vbo);
    glDeleteProgram(ren->shader);
}

void renderer_render(Renderer *ren, uint8_t *pixels) {
    glBindTexture(GL_TEXTURE_2D, ren->tex_id);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, ren->width, ren->height,
                    GL_RGB, GL_UNSIGNED_BYTE, pixels);
    glClear(GL_COLOR_BUFFER_BIT);
    glUseProgram(ren->shader);
    glBindVertexArray(ren->vao);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
}

void renderer_save_ppm(Renderer *ren, uint8_t *pixels, const char *filename) {
    FILE *f = fopen(filename, "wb");
    if (!f) return;
    fprintf(f, "P6\n%d %d\n255\n", ren->width, ren->height);
    fwrite(pixels, 3, ren->width * ren->height, f);
    fclose(f);
    printf("Screenshot saved: %s\n", filename);
}
