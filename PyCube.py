""" PyCube
Author: Michael King

Based and modified from original version found at:
http://stackoverflow.com/questions/30745703/rotating-a-cube-using-quaternions-in-pyopengl
"""

from quat import *
from geometry import *
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('PyCube')

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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Rotating about the x axis
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    inc_x = pi / 100
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    inc_x = -pi / 100

                # Rotating about the y axis
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    inc_y = pi / 100
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    inc_y = -pi / 100

                if event.key == pygame.K_u:
                    print('up')
                    rotateFace(inc_x, pi / 450, accum, zoom)

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
                                event.key == pygame.K_u:
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

        pygame.mouse.get_rel()  # prevents the cube from instantly rotating to a newly clicked mouse coordinate

        rot_x = normalize(axisangle_to_q((1.0, 0.0, 0.0), inc_x))
        rot_y = normalize(axisangle_to_q((0.0, 1.0, 0.0), inc_y))

        accum = q_mult(accum, rot_x)
        accum = q_mult(accum, rot_y)

        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(q_to_mat4(accum))
        glScalef(zoom, zoom, zoom)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube()
        # axis()
        pygame.display.flip()
        # pygame.time.wait(1)


main()
