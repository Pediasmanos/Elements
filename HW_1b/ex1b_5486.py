"""
Exercise 1b -- The doors of the Parthenon :: STARTER (finish it and rename it: XXXX = your AM, e.g. ex1b_1234.py)

Read ex1b.md first. Run it now: you get the grid, the axes, a given cube and a given cylinder.
Your work is marked TODO, in order:  1 the prism   2 the temple   3 the normals   4 the doors.

    python ex1b_XXXX.py
"""
import numpy as np
import time

import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, RenderMesh
from Elements.pyECSS.System import TransformSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator2
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.utils.terrain import generateTerrain
import Elements.utils.normals as norm
from Elements.definitions import SHADER_DIR

from OpenGL.GL import GL_LINES

from lab_lighting import apply_lighting      # given to you: the light

winWidth = 1200
winHeight = 800

scene = Scene()

# Scenegraph: everything hangs below the root
rootEntity = scene.world.createEntity(Entity(name="RooT"))

# Systems
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
initUpdate = scene.world.createSystem(InitGLShaderSystem())
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())


## TERRAIN: a grid on the xz plane. One square of the grid is one unit ##
vertexTerrain, indexTerrain, colorTerrain = generateTerrain(size=8)
terrain = scene.world.createEntity(Entity(name="terrain"))
scene.world.addEntityChild(rootEntity, terrain)
terrain_trans = scene.world.addComponent(terrain, BasicTransform(name="terrain_trans", trs=util.identity()))
terrain_mesh = scene.world.addComponent(terrain, RenderMesh(name="terrain_mesh"))
terrain_mesh.vertex_attributes.append(vertexTerrain)
terrain_mesh.vertex_attributes.append(colorTerrain)
terrain_mesh.vertex_index.append(indexTerrain)
terrain_vArray = scene.world.addComponent(terrain, VertexArray(primitive=GL_LINES))
terrain_shader = scene.world.addComponent(terrain, ShaderGLDecorator(
    Shader(vertex_import_file=SHADER_DIR / "ColorMVP.vert", fragment_import_file=SHADER_DIR / "Color.frag")))

## AXES: x is red, y is green, z is blue ##
vertexAxes = np.array([
    [0.0, 0.0, 0.0, 1.0], [3.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0], [0.0, 3.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 3.0, 1.0]
], dtype=np.float32)
colorAxes = np.array([
    [1.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
indexAxes = np.array((0, 1, 2, 3, 4, 5), np.uint32)

axes = scene.world.createEntity(Entity(name="axes"))
scene.world.addEntityChild(rootEntity, axes)
axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.002, 0.0)))   # a hair above the grid
axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))
axes_mesh.vertex_attributes.append(vertexAxes)
axes_mesh.vertex_attributes.append(colorAxes)
axes_mesh.vertex_index.append(indexAxes)
axes_vArray = scene.world.addComponent(axes, VertexArray(primitive=GL_LINES))
axes_shader = scene.world.addComponent(axes, ShaderGLDecorator(
    Shader(vertex_import_file=SHADER_DIR / "ColorMVP.vert", fragment_import_file=SHADER_DIR / "Color.frag")))

# ==========================================================================================
# MESHES. A mesh is a few arrays, one row per vertex: positions (x, y, z, 1)
# and an index list that says which three vertices make a triangle.
# ==========================================================================================

# ---- GIVEN: the cube, 1 x 1 x 1, centred on the origin (x, y, z from -0.5 to 0.5) ----
#
#         7 ------- 6
#        /|        /|          vertices 0-3 are the front face (z = +0.5), 4-7 the back face (z = -0.5)
#       3 ------- 2 |          (0 is bottom left, 1 bottom right, 2 top right, 3 top left)
#       | 4 -----|- 5
#       |/        |/
#       0 ------- 1
vertexCube = np.array([
    [-0.5, -0.5,  0.5, 1.0],     # 0
    [ 0.5, -0.5,  0.5, 1.0],     # 1
    [ 0.5,  0.5,  0.5, 1.0],     # 2
    [-0.5,  0.5,  0.5, 1.0],     # 3
    [-0.5, -0.5, -0.5, 1.0],     # 4
    [ 0.5, -0.5, -0.5, 1.0],     # 5
    [ 0.5,  0.5, -0.5, 1.0],     # 6
    [-0.5,  0.5, -0.5, 1.0]      # 7
], dtype=np.float32)

indexCube = np.array((0, 1, 2,  0, 2, 3,       # front
                      5, 4, 7,  5, 7, 6,       # back
                      4, 5, 1,  4, 1, 0,       # bottom
                      3, 2, 6,  3, 6, 7,       # top
                      1, 5, 6,  1, 6, 2,       # right
                      4, 0, 3,  4, 3, 7), np.uint32)   # left

# ---- GIVEN: the cylinder, radius 1, 1 high, standing along y (y from -0.5 to 0.5) ----
SEGMENTS = 24                    # the more segments, the rounder the circle

vertexCylinder = []
for i in range(SEGMENTS):
    angle = 2 * np.pi * i / SEGMENTS
    x = np.cos(angle)
    z = -np.sin(angle)                           # minus: so that the triangles below keep facing outwards
    vertexCylinder.append([x,  0.5, z, 1.0])     # vertex 2*i      : on the circle, top face
    vertexCylinder.append([x, -0.5, z, 1.0])     # vertex 2*i + 1  : on the circle, bottom face
vertexCylinder.append([0.0,  0.5, 0.0, 1.0])     # vertex 2*SEGMENTS      : centre of the top face
vertexCylinder.append([0.0, -0.5, 0.0, 1.0])     # vertex 2*SEGMENTS + 1  : centre of the bottom face
vertexCylinder = np.array(vertexCylinder, dtype=np.float32)

indexCylinder = []
for i in range(SEGMENTS):
    j = (i + 1) % SEGMENTS                       # the next vertex around the circle
    indexCylinder += [2*i, 2*i + 1, 2*j + 1,   2*i, 2*j + 1, 2*j]    # the side: two triangles
    indexCylinder += [2 * SEGMENTS, 2*i, 2*j]                        # top face: one triangle (like a pizza slice)
    indexCylinder += [2 * SEGMENTS + 1, 2*j + 1, 2*i + 1]            # bottom face
indexCylinder = np.array(indexCylinder, np.uint32)

# ---- TODO 1: the triangular prism (half of a unit cube: a right triangle with legs 1 and 1, 1 deep). ----
vertexPrism = np.array([
    [-0.5, -0.5,  0.5, 1.0],     # 0
    [ 0.5, -0.5,  0.5, 1.0],     # 1
    [-0.5,  0.5,  0.5, 1.0],     # 3,   2 sto array
    [-0.5, -0.5, -0.5, 1.0],     # 4    3 sto array
    [ 0.5, -0.5, -0.5, 1.0],     # 5    4 
    [-0.5,  0.5, -0.5, 1.0]      # 7    5
], dtype=np.float32)      # TODO: (x, y, z, 1.0) per vertex, float32

indexPrism = np.array((0, 1, 2, # front 
                       3, 5, 4,      # back face
                       3, 1, 0,  3, 4, 1,    # katw pleura
                       4, 2, 1,  4, 5, 2,    # h slide meria tou prism
                       2, 5, 3,  2, 3, 0,    # aristero face
                       
                                           
), dtype= np.uint32)      # TODO: three numbers per triangle, uint32, counter-clockwise seen from outside

# ==========================================================================================
# THE PARTHENON: one Entity with one transform. All the parts below are its children.
# ==========================================================================================
parthenon = scene.world.createEntity(Entity(name="parthenon"))
scene.world.addEntityChild(rootEntity, parthenon)
parthenon_trans = scene.world.addComponent(parthenon, BasicTransform(name="parthenon_trans", trs=util.identity()))

parts = []                     # (shader, transform) of every mesh we draw


def draw_shape(name, vertices, indices, color, trs):
    """Put a mesh in the scene, a child of the parthenon. `color` is [r, g, b, a]; `trs` says how big, how turned and where."""
    entity = scene.world.createEntity(Entity(name=name))
    scene.world.addEntityChild(parthenon, entity)
    trans = scene.world.addComponent(entity, BasicTransform(name=name + "_trans", trs=trs))
    mesh = scene.world.addComponent(entity, RenderMesh(name=name + "_mesh"))
    # TODO 3: this is the version WITHOUT normals (colours only, flat colour shader). Add the normals and the light.
    vertices, indices, color, normals = norm.generateFlatNormalsMesh(vertices, indices, np.array([color] * len(vertices), dtype=np.float32))
    
    mesh.vertex_attributes.append(vertices)
    mesh.vertex_attributes.append(color)
    mesh.vertex_index.append(indices)
    mesh.vertex_attributes.append(normals)
    scene.world.addComponent(entity, VertexArray())
    shader = scene.world.addComponent(entity, ShaderGLDecorator(
        Shader(vertex_import_file=SHADER_DIR / "Phong.vert", fragment_import_file=SHADER_DIR / "BlinnPhong.frag")))
    parts.append((shader, trans))
    return trans


def draw_cube(name, color, trs):
    return draw_shape(name, vertexCube, indexCube, color, trs)


def draw_cylinder(name, color, trs):
    return draw_shape(name, vertexCylinder, indexCylinder, color, trs)


def draw_prism(name, color, trs):
    return draw_shape(name, vertexPrism, indexPrism, color, trs)


stone = [0.80, 0.77, 0.70, 1.0]
marble = [0.93, 0.92, 0.88, 1.0]
terracotta = [0.72, 0.32, 0.20, 1.0]
bronze = [0.55, 0.36, 0.18, 1.0]

# the two given meshes, as they come. DELETE these two lines when you start TODO 2.
draw_cube("demo_cube", stone, util.translate(-3.0, 0.5, 6.0))
draw_cylinder("demo_cylinder", marble, util.translate(0.0, 0.5, 6.0))
draw_prism("test_prism", terracotta, util.translate(3.0, 0.5, 6.0))

# TODO 2: the temple, doors closed. Use draw_cube, draw_cylinder and draw_prism (name, color, matrix).
# Also: one unscaled cube, cylinder and prism, in front of the temple.
# Keep the two doors: door_left = draw_cube(...), door_right = draw_cube(...)
draw_cube("base", stone, util.translate(0.0, 0.25, 0.0) @ util.scale(10,0.5,3))
draw_cylinder("column1", marble, util.translate(-3.75, 0.5+ 2.5, 0.0) @ util.scale(0.5, 5, 0.5))
draw_cylinder("column2", marble, util.translate(3.75, 0.5+ 2.5, 0.0) @ util.scale(0.5, 5, 0.5))
draw_prism("roof1", terracotta, util.translate(2.75, 5.5+ 1, 0.0) @ util.scale(5.5, 2, 3.4))
draw_prism("roof2", terracotta, util.translate(-2.75, 5.5+ 1, 0.0) @ util.rotate((0,1,0),180) @util.scale(5.5, 2, 3.4))
door_left = draw_cube("door1", bronze, util.translate(-1.5625, 2.5 + 0.5, 0.0) @ util.scale(2.9,5,0.2))
door_right = draw_cube("door2", bronze, util.translate(1.5625, 2.5+ 0.5, 0.0) @ util.scale(2.9,5,0.2))


# ==========================================================================================
# WINDOW, EVENTS, CAMERA
# ==========================================================================================
scene.init(imgui=True, windowWidth=winWidth, windowHeight=winHeight, windowTitle="Elements: Exercise 1b - the Parthenon", customImGUIdecorator=ImGUIecssDecorator2, openGLversion=4)

# Everything created so far has to be sent to the GPU once (needs the window, i.e. an OpenGL context)
scene.world.traverse_visit(initUpdate, scene.world.root)

gWindow = scene.renderWindow          # the SDL2 window: pixels, mouse, keyboard, and the camera matrix
gGUI = scene.gContext               # the ImGui layer around it, which also owns the camera

# Camera: where we stand (eye), what we look at (target), which way is up
eye = util.vec(5.0, 6.5, 18.0)
target = util.vec(0.0, 3.5, 0.0)
up = util.vec(0.0, 1.0, 0.0)
gGUI.createViewMatrix(eye, target, up)                  # sets the camera (the mouse and the GUI move it from here)
projMat = util.perspective(50.0, winWidth / winHeight, 0.1, 100.0)

start_time = time.time()


# ==========================================================================================
# MAIN LOOP
# ==========================================================================================
running = True
while running:
    running = scene.render()                                          # window, events, GUI

    # TODO 4: the doors open and close. t is the time in seconds.
    t = time.time() - start_time
    door_left.trs =util.translate(-3.0125, 3.0, 0.0) @ util.rotate((0, 1, 0), -45 * (1-np.cos(2.5*t)))@ util.translate(1.45, 0.0, 0.0) @util.scale(2.9,5,0.2)
    door_right.trs =util.translate(3.0125, 3.0, 0.0) @ util.rotate((0, 1, 0), 45 * (1-np.cos(2.5*t)))@ util.translate(-1.45, 0.0, 0.0) @util.scale(2.9,5,0.2)

    scene.world.traverse_visit(transUpdate, scene.world.root)         # compute the world matrix (l2world) of every transform
    view = gWindow._myCamera                                           # the camera: moves with the mouse / the GUI
    terrain_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ terrain_trans.l2world, mat4=True)
    axes_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ axes_trans.l2world, mat4=True)
    for shader, trans in parts:
        shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ trans.l2world, mat4=True)
        # TODO 3: the light: apply_lighting(shader, trans.l2world, gWindow._cameraEye)
        apply_lighting(shader, trans.l2world, gWindow._cameraEye)

    scene.world.traverse_visit(renderUpdate, scene.world.root)        # draw everything
    scene.render_post()

scene.shutdown()
