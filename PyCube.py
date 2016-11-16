""" PyCube
Author: Michael King

Based and modified from original version found at:
http://stackoverflow.com/questions/30745703/rotating-a-cube-using-quaternions-in-pyopengl
"""
import sys
from quat import *
from geometry import *

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

'''
    5____________6
    /           /|
   /           / |
 1/__________2/  |
 |           |   |
 |           |   |
 |           |   7
 |           |  /
 |           | /
 0___________3/
'''

edge_pieces = [

    # [[-3, -1, 3],
    #  [-3, 1, 3],
    #  [-1, 1, 3],
    #  [-1, -1, 3],
    #  [-3, -1, 1],
    #  [-3, 1, 1],
    #  [-1, 1, 1],
    #  [-1, -1, 1]]

    # [[-3, -3, 1],
    #  [-3, -1, 1],
    #  [-1, -1, 1],
    #  [-1, -3, 1],
    #  [-3, -3, -1],
    #  [-3, -1, -1],
    #  [-1, -1, -1],
    #  [-1, -3, -1]]


]

center_pieces = [
    # Front 0
    [[-1, -1, 3],
     [-1, 1, 3],
     [1, 1, 3],
     [1, -1, 3],
     [-1, -1, 1],
     [-1, 1, 1],
     [1, 1, 1],
     [1, -1, 1]],

    # Left 1
    [[-3, -1, 1],
     [-3, 1, 1],
     [-1, 1, 1],
     [-1, -1, 1],
     [-3, -1, -1],
     [-3, 1, -1],
     [-1, 1, -1],
     [-1, -1, -1]],

    # Back 2
    [[-1, -1, -1],
     [-1, 1, -1],
     [1, 1, -1],
     [1, -1, -1],
     [-1, -1, -3],
     [-1, 1, -3],
     [1, 1, -3],
     [1, -1, -3],
     ],

    # Right 3
    [[1, -1, 1],
     [1, 1, 1],
     [3, 1, 1],
     [3, -1, 1],
     [1, -1, -1],
     [1, 1, -1],
     [3, 1, -1],
     [3, -1, -1],

     ],

    # Up 3
    [[-1, 1, 1],
     [-1, 3, 1],
     [1, 3, 1],
     [1, 1, 1],
     [-1, 1, -1],
     [-1, 3, -1],
     [1, 3, -1],
     [1, 1, -1]],

    # Down 4
    [[-1, -3, 1],
     [-1, -1, 1],
     [1, -1, 1],
     [1, -3, 1],
     [-1, -3, -1],
     [-1, -1, -1],
     [1, -1, -1],
     [1, -3, -1]]
]

'''
    These pattern are for each set of edge pieces and corner
    pieces on each face. They will shift when the faces are
    rotated so these patterns will keep track of them.
     _______________
    |  1 |  2 |  2 |
    |____|____|____|
    | 1  |    |  3 |
    |____|____|____|
    |  0 |  0 |  3 |
    |____|____|____|

'''
face_patterns = [
    [0, 1, 2, 3],  # 0 Front
    [0, 1, 2, 3],  # 1 Back
    [0, 1, 2, 3],  # 2 Left
    [0, 1, 2, 3],  # 3 Right
    [0, 1, 2, 3],  # 4 Up
    [0, 1, 2, 3],  # 5 Down
]


def draw_cube():
    glBegin(GL_LINES)
    glColor3fv((0.5, 0.5, 0.5))
    for piece in edge_pieces:
        for edge in cube_edges:
            for vertex in edge:
                glVertex3fv(piece[vertex])
    for piece in center_pieces:
        for edge in cube_edges:
            for vertex in edge:
                glVertex3fv(piece[vertex])
    glEnd()

    glBegin(GL_QUADS)
    # glColor3fv((0, 0, 0))
    # for surface in cube_surfaces:
    #     for piece in center_pieces:
    #         for vertex in surface:
    #             glVertex3fv(piece[vertex])
    i = 0

    for color, surface in zip(cube_colors, cube_surfaces):
        glColor3fv(color)
        for vertex in surface:
            glVertex3fv(center_pieces[i][vertex])
        j = 0
        for piece in center_pieces:
            glColor3fv((0, 0, 0))
            for vertex in surface:
                glVertex3fv(center_pieces[j][vertex])
            j += 1
        i += 1

    glEnd()


def main():
    pygame.init()
    display = (800, 600)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('PyCube')

    glClearColor(1, 1, 1, 0)
    # Using depth test to make sure closer colors are shown over further ones
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # Default view
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.5, 40)
    glTranslatef(0.0, 0.0, -17.5)

    # set initial rotation
    # glRotate(90, 1, 0, 0)
    # glRotate(-15, 0, 0, 1)
    # glRotate(15, 1, 0, 0)

    inc_x = 0
    inc_y = 0
    accum = (1, 0, 0, 0)
    zoom = 1

    def update():
        pygame.mouse.get_rel()  # prevents the cube from instantly rotating to a newly clicked mouse coordinate

        rot_x = normalize(axisangle_to_q((1.0, 0.0, 0.0), inc_x))
        rot_y = normalize(axisangle_to_q((0.0, 1.0, 0.0), inc_y))

        nonlocal accum
        accum = q_mult(accum, rot_x)
        accum = q_mult(accum, rot_y)
        # print(accum)

        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(q_to_mat4(accum))
        glScalef(zoom, zoom, zoom)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw_cube()
        # drawFace()
        axis()
        pygame.display.flip()
        # pygame.time.wait(1)

    # for v in left_face:
    #     print(v)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Rotating about the x axis
                if event.key == pygame.K_UP:  # or event.key == pygame.K_w:
                    inc_x = pi / 100
                if event.key == pygame.K_DOWN:  # or event.key == pygame.K_s:
                    inc_x = -pi / 100

                # Rotating about the y axis
                if event.key == pygame.K_LEFT:  # or event.key == pygame.K_a:
                    inc_y = pi / 100
                if event.key == pygame.K_RIGHT:  # or event.key == pygame.K_d:
                    inc_y = -pi / 100

                if event.key == pygame.K_f:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("F\'")
                        theta = 0.13089969389957471827
                    else:
                        sys.stdout.write("F")
                        theta = -0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[0][i] = z_rot(center_pieces[0][i], theta)
                        update()

                if event.key == pygame.K_l:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("L\'")
                        theta = -0.13089969389957471827
                    else:
                        sys.stdout.write("L")
                        theta = 0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[1][i] = x_rot(center_pieces[1][i], theta)
                        update()

                if event.key == pygame.K_b:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("B\'")
                        theta = -0.13089969389957471827
                    else:
                        sys.stdout.write("B")
                        theta = 0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[2][i] = z_rot(center_pieces[2][i], theta)
                        update()

                if event.key == pygame.K_r:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("R\'")
                        theta = 0.13089969389957471827
                    else:
                        sys.stdout.write("R")
                        theta = -0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[3][i] = x_rot(center_pieces[3][i], theta)
                        update()

                if event.key == pygame.K_u:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("U\'")
                        theta = 0.13089969389957471827
                    else:
                        sys.stdout.write("U")
                        theta = -0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[4][i] = y_rot(center_pieces[4][i], theta)
                        update()

                if event.key == pygame.K_d:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        sys.stdout.write("D\'")
                        theta = -0.13089969389957471827
                    else:
                        sys.stdout.write("D")
                        theta = 0.13089969389957471827
                    for x in range(12):
                        for i in range(8):
                            center_pieces[5][i] = y_rot(center_pieces[5][i], theta)
                        update()

                # Reset to default view
                if event.key == pygame.K_SPACE:
                    inc_x = 0
                    inc_y = 0
                    accum = (1, 0, 0, 0)
                    zoom = 1

            if event.type == pygame.KEYUP:
                # Stoping rotation
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or \
                                event.key == pygame.K_w or event.key == pygame.K_s:
                    inc_x = 0.0
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or \
                                event.key == pygame.K_a or event.key == pygame.K_d or \
                                event.key == pygame.K_l or event.key == pygame.K_f:
                    inc_y = 0.0

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Increase scale (zoom) value
                if event.button == 4:
                    if zoom < 1.6:
                        zoom += 0.05
                        # print('scroll up', zoom)
            if event.type == pygame.MOUSEBUTTONUP:
                # Increase scale (zoom) value
                if event.button == 5:
                    if zoom > 0.2:
                        zoom -= 0.05
                        # print('scroll down', zoom)

        # Get relative movement of mouse coordinates and update x and y incs
        if pygame.mouse.get_pressed()[0] == 1:
            (tmp_x, tmp_y) = pygame.mouse.get_rel()
            # print(tmp_x, tmp_y)
            inc_x = -tmp_y * pi / 450
            inc_y = -tmp_x * pi / 450

        update()
        sys.stdout.flush()


main()