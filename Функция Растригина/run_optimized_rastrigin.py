import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from swarm_rastrigin import SwarmRastrigin  # Подкласс роя частиц для Растригина
from utils import printResult  # Функция для вывода результатов
import tkinter as tk
from tkinter import messagebox
from threading import Thread

# Глобальные переменные для управления вращением и камерами
rotation_x = 0
rotation_y = 0
last_mouse_x = 0
last_mouse_y = 0
mouse_dragging = False
camera_distance = 80  # Начальное расстояние камеры от сцены

# Параметры оптимизации
iterCount = 300
dimension = 2
swarmsize = 2000

minvalues = [-5.12] * dimension
maxvalues = [5.12] * dimension
currentVelocityRatio = 0.5
localVelocityRatio = 2.0
globalVelocityRatio = 5.0

# Функция Растригина
def rastrigin_function(x, y):
    A = 10
    return A * 2 + (x ** 2 - A * np.cos(2 * np.pi * x)) + (y ** 2 - A * np.cos(2 * np.pi * y))

# Отрисовка поверхности функции Растригина
def draw_surface(X, Y, Z):
    glBegin(GL_QUADS)
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            color_value_1 = 0.5 + 0.5 * Z[i, j] / Z.max()
            color_value_2 = 0.5 + 0.5 * Z[i + 1, j] / Z.max()
            color_value_3 = 0.5 + 0.5 * Z[i + 1, j + 1] / Z.max()
            color_value_4 = 0.5 + 0.5 * Z[i, j + 1] / Z.max()

            glColor3f(0.2, color_value_1, 0.8)
            glVertex3f(X[i, j], Y[i, j], Z[i, j])

            glColor3f(0.2, color_value_2, 0.8)
            glVertex3f(X[i + 1, j], Y[i, j], Z[i + 1, j])

            glColor3f(0.2, color_value_3, 0.8)
            glVertex3f(X[i + 1, j + 1], Y[i, j + 1], Z[i + 1, j + 1])

            glColor3f(0.2, color_value_4, 0.8)
            glVertex3f(X[i, j + 1], Y[i, j + 1], Z[i, j + 1])
    glEnd()

# Отрисовка осей
def draw_axes():
    glLineWidth(2)

    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)

    glVertex3f(-1000, 0, 0)
    glVertex3f(1000, 0, 0)

    glVertex3f(0, -1000, 0)
    glVertex3f(0, 1000, 0)

    glVertex3f(0, 0, -1000)
    glVertex3f(0, 0, 1000)
    glEnd()

    glLineWidth(1)
    glBegin(GL_LINES)

    for i in np.arange(-10, 10, 1):
        glVertex3f(i, -0.1, 0)
        glVertex3f(i, 0.1, 0)

    for i in np.arange(-10, 10, 1):
        glVertex3f(-0.1, i, 0)
        glVertex3f(0.1, i, 0)

    for i in np.arange(-10, 10, 1):
        glVertex3f(0, -0.1, i)
        glVertex3f(0, 0.1, i)

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

# Обработчик прокрутки мыши для изменения расстояния камеры
def scroll_callback(window, xoffset, yoffset):
    global camera_distance
    camera_distance += yoffset * 2  # Умножаем на 2 для ускорения изменения
    camera_distance = max(10, min(200, camera_distance))  # Ограничиваем расстояние камеры

# Основная функция для OpenGL визуализации
def run_opengl_visualization():
    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    window_3d = glfw.create_window(800, 600, "Swarm Optimization on Rastrigin Function", None, None)
    if not window_3d:
        glfw.terminate()
        print("Не удалось создать окно для 3D-визуализации")
        return

    # Второе окно для 2D-визуализации
    window_2d = glfw.create_window(800, 600, "2D Swarm Visualization", None, None)
    if not window_2d:
        glfw.terminate()
        print("Не удалось создать окно для 2D-визуализации")
        return

    glfw.make_context_current(window_3d)
    glfw.set_cursor_pos_callback(window_3d, mouse_motion_callback)
    glfw.set_mouse_button_callback(window_3d, mouse_button_callback)
    glfw.set_scroll_callback(window_3d, scroll_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    swarm = SwarmRastrigin(
        swarmsize,
        minvalues,
        maxvalues,
        currentVelocityRatio,
        localVelocityRatio,
        globalVelocityRatio,
    )

    x = np.linspace(-5.12, 5.12, 100)
    y = np.linspace(-5.12, 5.12, 100)

    X, Y = np.meshgrid(x, y)
    Z = rastrigin_function(X, Y)
    Z = Z - np.min(Z)

    for n in range(iterCount):
        glfw.make_context_current(window_3d)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluPerspective(45, 800 / 600, 0.1, 250)
        gluLookAt(camera_distance, camera_distance, camera_distance, 0, 0, 0, 0, 1, 0)

        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        draw_axes()
        draw_surface(X, Y, Z)

        positions = np.array([particle.position for particle in swarm])
        glColor3f(1.0, 0.0, 0.0)
        glPointSize(8)
        glBegin(GL_POINTS)
        for pos in positions:
            glVertex3f(pos[0], pos[1], rastrigin_function(pos[0], pos[1]))
        glEnd()

        swarm.nextIteration()

        print(printResult(swarm, n))

        glfw.swap_buffers(window_3d)
        glfw.poll_events()

        # 2D-визуализация
        glfw.make_context_current(window_2d)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(-5.12, 5.12, -5.12, 5.12, -1, 1)

        draw_particles_2d(swarm)

        glfw.swap_buffers(window_2d)
        glfw.poll_events()

    glfw.terminate()

# Функция для запуска программы через Tkinter
def start_optimization():
    global iterCount, dimension, swarmsize, currentVelocityRatio, localVelocityRatio, globalVelocityRatio

    try:
        iterCount = int(iter_count_entry.get())

        swarmsize = int(swarmsize_entry.get())
        currentVelocityRatio = float(velocity_inertia_entry.get())
        localVelocityRatio = float(velocity_personal_entry.get())
        globalVelocityRatio = float(velocity_global_entry.get())

        if dimension != 2:
            messagebox.showerror("Ошибка", "В текущей версии поддерживается только двумерное пространство!")
            return

        thread = Thread(target=run_opengl_visualization)
        thread.start()
    except ValueError:
        messagebox.showerror("Ошибка", "Все параметры должны быть числовыми!")

# Создание окна Tkinter
root = tk.Tk()
root.title("Swarm Optimization")

# Поля для ввода параметров
tk.Label(root, text="Количество итераций:").pack()
iter_count_entry = tk.Entry(root)
iter_count_entry.insert(0, str(iterCount))
iter_count_entry.pack()


tk.Label(root, text="Размер роя:").pack()
swarmsize_entry = tk.Entry(root)
swarmsize_entry.insert(0, str(swarmsize))
swarmsize_entry.pack()

tk.Label(root, text="Коэффициент инерции:").pack()
velocity_inertia_entry = tk.Entry(root)
velocity_inertia_entry.insert(0, str(currentVelocityRatio))
velocity_inertia_entry.pack()

tk.Label(root, text="Коэффициент личного опыта:").pack()
velocity_personal_entry = tk.Entry(root)
velocity_personal_entry.insert(0, str(localVelocityRatio))
velocity_personal_entry.pack()

tk.Label(root, text="Коэффициент глобального опыта:").pack()
velocity_global_entry = tk.Entry(root)
velocity_global_entry.insert(0, str(globalVelocityRatio))
velocity_global_entry.pack()

# Кнопка для запуска визуализации
start_button = tk.Button(root, text="Начать визуализацию", command=start_optimization)
start_button.pack(pady=20)

root.mainloop()
