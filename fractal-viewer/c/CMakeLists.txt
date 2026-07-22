cmake_minimum_required(VERSION 3.10)
project(fractal-viewer C)

find_package(OpenGL REQUIRED)
find_package(SDL2 REQUIRED)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -march=native -mtune=native -pthread")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffast-math -ftree-vectorize")

add_executable(fractal-viewer
    src/main.c
    src/fractal.c
    src/viewport.c
    src/palette.c
    src/renderer.c
    src/worker.c
)

target_link_libraries(fractal-viewer
    ${OPENGL_gl_LIBRARY}
    SDL2::SDL2
    m
    pthread
)

target_include_directories(fractal-viewer PRIVATE src)
