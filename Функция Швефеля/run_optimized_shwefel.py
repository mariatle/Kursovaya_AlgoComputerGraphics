import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from swarm_schwefel import SwarmSchwefel
from utils import printResult

# Глобальные переменные для управления вращением
rotation_x = 0
rotation_y = 0
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False
camera_distance = 80  # Расстояние камеры от сцены

# Параметры оптимизации
iterCount = 100
dimension = 3
swarmsize = 5000

minvalues = [-500.0] * dimension
maxvalues = [500.0] * dimension
currentVelocityRatio = 0.5
localVelocityRatio = 2.0
globalVelocityRatio = 5.0

# Функция Швефеля
def schwefel_function(x, y):
    return 418.9829 * 2 - (x * np.sin(np.sqrt(np.abs(x))) + y * np.sin(np.sqrt(np.abs(y))))

# Отрисовка поверхности функции Швефеля
def draw_surface(X, Y, Z):
    glBegin(GL_QUADS)
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            glColor3f(0.2, 0.5, 0.8)  # Цвет поверхности
            glVertex3f(X[i, j], Y[i, j], Z[i, j])
            glVertex3f(X[i + 1, j], Y[i, j], Z[i + 1, j])
            glVertex3f(X[i + 1, j + 1], Y[i, j + 1], Z[i + 1, j + 1])
            glVertex3f(X[i, j + 1], Y[i, j + 1], Z[i, j + 1])
    glEnd()

# Отрисовка осей с разметкой
def draw_axes():
    glLineWidth(2)
    glBegin(GL_LINES)

    # Ось X (красная)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-10000, 0, 0)
    glVertex3f(10000, 0, 0)

    # Ось Y (зелёная)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(0, -10000, 0)
    glVertex3f(0, 10000, 0)

    # Ось Z (синяя)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(0, 0, -10000)
    glVertex3f(0, 0, 10000)

    glEnd()

# Отрисовка частиц в 2D
def draw_particles_2d(swarm):
    positions = np.array([particle.position for particle in swarm])
    glColor3f(1.0, 0.0, 0.0)  # Красный цвет для частиц
    glPointSize(5)
    glBegin(GL_POINTS)
    for pos in positions:
        glVertex2f(pos[0], pos[1])  # Используем только x и y для 2D
    glEnd()

# Обработчик движения мыши
def mouse_motion_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y, rotation_x, rotation_y, mouse_dragging
    if mouse_dragging:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y
        rotation_x += dy * 0.5
        rotation_y += dx * 0.5
        last_mouse_x = xpos
        last_mouse_y = ypos

# Обработчик кнопок мыши
def mouse_button_callback(window, button, action, mods):
    global last_mouse_x, last_mouse_y, mouse_dragging
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_dragging = True
            last_mouse_x, last_mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            mouse_dragging = False

# Основная функция
def main():
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    # Создаём первое окно для 3D-визуализации
    window_3d = glfw.create_window(800, 600, "3D Swarm Optimization on Schwefel Function", None, None)
    if not window_3d:
        glfw.terminate()
        print("Не удалось создать окно для 3D-визуализации")
        return

    # Создаём второе окно для 2D-визуализации
    window_2d = glfw.create_window(800, 600, "2D Swarm Visualization", None, None)
    if not window_2d:
        glfw.terminate()
        print("Не удалось создать окно для 2D-визуализации")
        return

    glfw.make_context_current(window_3d)
    glfw.set_cursor_pos_callback(window_3d, mouse_motion_callback)
    glfw.set_mouse_button_callback(window_3d, mouse_button_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Создаём рой частиц
    swarm = SwarmSchwefel(
        swarmsize,
        minvalues,
        maxvalues,
        currentVelocityRatio,
        localVelocityRatio,
        globalVelocityRatio,
    )

    # Создаём сетку для визуализации функции Швефеля
    x = np.linspace(-500, 500, 200)
    y = np.linspace(-500, 500, 200)

    X, Y = np.meshgrid(x, y)
    Z = schwefel_function(X, Y)

    for n in range(iterCount):
        # Обновляем 3D-окно
        glfw.make_context_current(window_3d)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        gluPerspective(45, 800 / 600, 0.1, 2500)
        gluLookAt(1200, 1200, 1200, 0, 0, 0, 0, 1, 0)

        # Вращение сцены
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        # Рисуем оси
        draw_axes()

        # Рисуем поверхность функции Швефеля
        draw_surface(X, Y, Z)

        # Рисуем 3D частицы
        positions = np.array([particle.position for particle in swarm])
        glColor3f(1.0, 0.0, 0.0)  # Красный цвет для частиц
        glPointSize(8)
        glBegin(GL_POINTS)
        for pos in positions:
            glVertex3f(pos[0], pos[1], schwefel_function(pos[0], pos[1]))
        glEnd()

        # Обновляем рой частиц
        swarm.nextIteration()

        # Выводим информацию об итерации
        print(printResult(swarm, n))

        glfw.swap_buffers(window_3d)
        glfw.poll_events()

        # Обновляем 2D-окно
        glfw.make_context_current(window_2d)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # Устанавливаем ортогональную проекцию для 2D
        glOrtho(-500, 500, -500, 500, -1, 1)  # 2D пространство для частиц
        glViewport(0, 0, 800, 600)  # Размеры окна 2D

        # Рисуем 2D частицы
        draw_particles_2d(swarm)

        glfw.swap_buffers(window_2d)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
