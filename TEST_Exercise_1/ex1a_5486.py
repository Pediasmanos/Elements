"""
Exercise 1a -- The LEGO builder :: STARTER (finish it and rename it: XXXX = your AM, e.g. ex1a_1234.py)

Read ex1a.md first. Run it now: you get the grid, the axes, a given cube and a given cylinder.
Your work is marked TODO, in order:  1 draw_lego   2 the panel   3 add / delete   4 the first legos.

    python ex1a_XXXX.py
"""
import numpy as np
import time
import imgui

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


## TERRAIN: the build plate, 16 x 16 cells on the xz plane. One square of the grid is one unit (one stud) ##
vertexTerrain, indexTerrain, colorTerrain = generateTerrain(size=8)
terrain = scene.world.createEntity(Entity(name="terrain"))
scene.world.addEntityChild(rootEntity, terrain)
terrain_trans = scene.world.addComponent(terrain, BasicTransform(name="terrain_trans", trs=util.translate(8.0, 0.0, 8.0)))   # moved so that the plate spans x, z from 0 to 16
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

# ==========================================================================================
# DRAWING. Every mesh is lit (flat normals + apply_lighting), so it is drawn with the Phong shader.
# ==========================================================================================
parts = []                     # (shader, transform, parent entity) of every mesh we draw

red = [0.80, 0.10, 0.12, 1.0]
orange = [0.93, 0.45, 0.08, 1.0]
yellow = [0.98, 0.78, 0.08, 1.0]
green = [0.13, 0.55, 0.24, 1.0]
blue = [0.02, 0.35, 0.68, 1.0]
white = [0.95, 0.95, 0.95, 1.0]
black = [0.12, 0.12, 0.14, 1.0]


def draw_shape(parent, name, vertices, indices, color, trs):
    """Put a mesh in the scene, a child of `parent`. `color` is [r, g, b, a]; `trs` says how big, how turned and where."""
    entity = scene.world.createEntity(Entity(name=name))
    scene.world.addEntityChild(parent, entity)
    trans = scene.world.addComponent(entity, BasicTransform(name=name + "_trans", trs=trs))
    mesh = scene.world.addComponent(entity, RenderMesh(name=name + "_mesh"))
    v, i, c, n = norm.generateFlatNormalsMesh(vertices, indices, np.array([color] * len(vertices), dtype=np.float32))
    mesh.vertex_attributes.append(v)         # position
    mesh.vertex_attributes.append(c)         # colour
    mesh.vertex_attributes.append(n)         # normal
    mesh.vertex_index.append(i)
    scene.world.addComponent(entity, VertexArray())
    shader = scene.world.addComponent(entity, ShaderGLDecorator(
        Shader(vertex_import_file=SHADER_DIR / "Phong.vert", fragment_import_file=SHADER_DIR / "BlinnPhong.frag")))
    parts.append((shader, trans, parent))
    return trans


def draw_cube(parent, name, color, trs):
    return draw_shape(parent, name, vertexCube, indexCube, color, trs)


def draw_cylinder(parent, name, color, trs):
    return draw_shape(parent, name, vertexCylinder, indexCylinder, color, trs)


# ---- TODO 1: draw_lego (see ex1a.md) ----
def draw_lego(name, n, m, color, i, j, layer):
    """Put an n x m lego in the scene, in cells i.. and j.., on the given layer. Returns its Entity."""
    lego = scene.world.createEntity(Entity(name=name))
    scene.world.addEntityChild(rootEntity, lego)
    scene.world.addComponent(lego, BasicTransform(name=name + "_trans", trs=util.translate(i, layer * 1.2, j) @ util.identity()))   # kanw to translate edw, wste ta kommatia tou entity na einai sxetika me to lego kai oxi me to rootEntity
    # TODO: the body: draw_cube(lego, ...)
    draw_cube(lego, name + "_body", color, util.translate(n/2, 0.6, m/2) @ util.scale(n, 1.2, m))
    #draw_cube(lego, name + "_body", color, util.translate(i + n/2, layer*1.2 + 0.6, j + m/2) @ util.scale(n, 1.2, m))
    # TODO: the n * m studs: draw_cylinder(lego, ...)
    for x in range(n):
        for y in range(m):
            draw_cylinder(lego, name+ "_stud_"+ str(x)+"_"+str(y), color, util.translate(x + 0.5, 1.2+ 0.1125, y + 0.5) @ util.scale(0.3,0.225,0.3))
    return lego


legos = []                     # the legos on the scene, in the order they were placed

# the two given meshes, as they come. DELETE these two lines when you start TODO 1.
#draw_cube(rootEntity, "demo_cube", white, util.translate(4.0, 0.5, 4.0))
#draw_cylinder(rootEntity, "demo_cylinder", red, util.translate(8.0, 0.5, 4.0))

# TODO 4: the first legos, with draw_lego, each one app`ended to `legos`.

legos.append(draw_lego("lego1", 4, 2, red, 0, 0, 0))
legos.append(draw_lego("lego2", 2, 2, blue, 4, 0, 0))
legos.append(draw_lego("lego3", 2, 4, yellow, 0, 2, 0))
legos.append(draw_lego("lego4", 4, 2, green, 2, 2, 0))
legos.append(draw_lego("lego5", 2, 2, white, 1, 0, 1))
legos.append(draw_lego("lego6", 1, 1, orange, 4, 0, 1))

# ==========================================================================================
# WINDOW, EVENTS, CAMERA
# ==========================================================================================
scene.init(imgui=True, windowWidth=winWidth, windowHeight=winHeight, windowTitle="Elements: Exercise 1a - the LEGO builder", customImGUIdecorator=ImGUIecssDecorator2, openGLversion=4)

# Everything created so far has to be sent to the GPU once (needs the window, i.e. an OpenGL context)
scene.world.traverse_visit(initUpdate, scene.world.root)

gWindow = scene.renderWindow          # the SDL2 window: pixels, mouse, keyboard, and the camera matrix
gGUI = scene.gContext               # the ImGui layer around it, which also owns the camera

# Camera: where we stand (eye), what we look at (target), which way is up
eye = util.vec(6.0, 11.0, 19.0)
target = util.vec(6.0, 0.0, 4.0)
up = util.vec(0.0, 1.0, 0.0)
gGUI.createViewMatrix(eye, target, up)                  # sets the camera (the mouse and the GUI move it from here)
projMat = util.perspective(50.0, winWidth / winHeight, 0.1, 100.0)


# ==========================================================================================
# MAIN LOOP
# ==========================================================================================
running = True
while running:
    running = scene.render()                                          # window, events, GUI

    # TODO 2 and 3: the panel (imgui.begin(...) ... imgui.end()), Add and Delete last.
    imgui.begin("LEGO builder")
    imgui.button("Add")
    if(imgui.button("Delete last")):
        if(len(legos) > 0):
            last_lego = legos.pop()
            
    imgui.end()

    scene.world.traverse_visit(transUpdate, scene.world.root)         # compute the world matrix (l2world) of every transform
    view = gWindow._myCamera                                           # the camera: moves with the mouse / the GUI
    terrain_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ terrain_trans.l2world, mat4=True)
    axes_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ axes_trans.l2world, mat4=True)
    for shader, trans, parent in parts:
        shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ trans.l2world, mat4=True)
        apply_lighting(shader, trans.l2world, gWindow._cameraEye)     # the light (given)

    scene.world.traverse_visit(renderUpdate, scene.world.root)        # draw everything
    scene.render_post()

scene.shutdown()
