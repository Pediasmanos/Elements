import numpy as np
from pathlib import Path

import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, RenderMesh
from Elements.pyECSS.System import TransformSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator2
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.pyGLV.GL.Textures import Texture
from Elements.utils.terrain import generateTerrain
from Elements.definitions import SHADER_DIR

from OpenGL.GL import GL_LINES

winWidth = 1200
winHeight = 800

ATLAS = Path(__file__).resolve().parent / "pyramid_atlas.png"

scene = Scene()

rootEntity = scene.world.createEntity(Entity(name="RooT"))

transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
initUpdate = scene.world.createSystem(InitGLShaderSystem())
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())

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
axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.002, 0.0)))
axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))
axes_mesh.vertex_attributes.append(vertexAxes)
axes_mesh.vertex_attributes.append(colorAxes)
axes_mesh.vertex_index.append(indexAxes)
axes_vArray = scene.world.addComponent(axes, VertexArray(primitive=GL_LINES))
axes_shader = scene.world.addComponent(axes, ShaderGLDecorator(
    Shader(vertex_import_file=SHADER_DIR / "ColorMVP.vert", fragment_import_file=SHADER_DIR / "Color.frag")))

vertex_shader = """
#version 410

layout (location=0) in vec4 vPos;
layout (location=1) in vec2 vTexCoord;

out vec2 fragmentTexCoord;

uniform mat4 model;
uniform mat4 View;
uniform mat4 Proj;

void main()
{
    gl_Position = Proj * View * model * vPos;
    fragmentTexCoord = vTexCoord;
}
"""

fragment_shader = """
#version 410

in vec2 fragmentTexCoord;
out vec4 outputColor;

uniform sampler2D ImageTexture;

void main()
{
    outputColor = texture(ImageTexture, fragmentTexCoord);
}
"""

vertices = np.array([
    [-1.0, 0.0, 1.0, 1.0], [1.0, 0.0, 1.0, 1.0], [0.0, 2.5, 0.0, 1.0],
    [1.0, 0.0, 1.0, 1.0], [1.0, 0.0, -1.0, 1.0], [0.0, 2.5, 0.0, 1.0],
    [1.0, 0.0, -1.0, 1.0], [-1.0, 0.0, -1.0, 1.0], [0.0, 2.5, 0.0, 1.0],
    [-1.0, 0.0, -1.0, 1.0], [-1.0, 0.0, 1.0, 1.0], [0.0, 2.5, 0.0, 1.0],
], dtype=np.float32)
texcoords = np.array([
    [48.0/1024.0, 435.0/1024.0], [464.0/1024.0, 435.0/1024.0], [256.0/1024.0, 60.0/1024.0],
    [976.0/1024.0, 435.0/1024.0], [560.0/1024.0, 435.0/1024.0], [768.0/1024.0, 60.0/1024.0],
    [48.0/1024.0, 947.0/1024.0], [464.0/1024.0, 947.0/1024.0], [256.0/1024.0, 572.0/1024.0],
    [560.0/1024.0, 947.0/1024.0], [976.0/1024.0, 947.0/1024.0], [768.0/1024.0, 572.0/1024.0],
], dtype=np.float32)
indices = np.arange(12, dtype=np.uint32)

pyramid = scene.world.createEntity(Entity(name="pyramid"))
scene.world.addEntityChild(rootEntity, pyramid)
pyramid_trans = scene.world.addComponent(pyramid, BasicTransform(name="pyramid_trans", trs=util.identity()))
pyramid_mesh = scene.world.addComponent(pyramid, RenderMesh(name="pyramid_mesh"))
pyramid_mesh.vertex_attributes.append(vertices)
pyramid_mesh.vertex_attributes.append(texcoords)
pyramid_mesh.vertex_index.append(indices)
pyramid_vArray = scene.world.addComponent(pyramid, VertexArray())
pyramid_shader = scene.world.addComponent(pyramid, ShaderGLDecorator(
    Shader(vertex_source=vertex_shader, fragment_source=fragment_shader)))


def createSquare(name, x, z, square_texcoords):
    square_vertices = np.array([
        [-1.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 1.0],
        [1.0, 2.0, 0.0, 1.0],
        [-1.0, 2.0, 0.0, 1.0],
    ], dtype=np.float32)
    square_indices = np.array((0, 1, 2, 0, 2, 3), dtype=np.uint32)
    entity = scene.world.createEntity(Entity(name=name))
    scene.world.addEntityChild(rootEntity, entity)
    trans = scene.world.addComponent(entity, BasicTransform(name=name + "_trans", trs=util.translate(x, 0.0, z) @ util.rotate((0.0, 1.0, 0.0), 62.0)))
    mesh = scene.world.addComponent(entity, RenderMesh(name=name + "_mesh"))
    mesh.vertex_attributes.append(square_vertices)
    mesh.vertex_attributes.append(square_texcoords)
    mesh.vertex_index.append(square_indices)
    scene.world.addComponent(entity, VertexArray())
    shader = scene.world.addComponent(entity, ShaderGLDecorator(
        Shader(vertex_source=vertex_shader, fragment_source=fragment_shader)))
    return trans, shader


square_trans, square_shader = createSquare("square", -3.2, -0.6, np.array([
    [0.0, 3.0],
    [3.0, 3.0],
    [3.0, 0.0],
    [0.0, 0.0],
], dtype=np.float32))

scene.init(imgui=True, windowWidth=winWidth, windowHeight=winHeight, windowTitle="Elements: Live 2A - the pyramid and the square", customImGUIdecorator=ImGUIecssDecorator2, openGLversion=4)

scene.world.traverse_visit(initUpdate, scene.world.root)

gWindow = scene.renderWindow
gGUI = scene.gContext

eye = util.vec(4.0, 3.5, 5.0)
target = util.vec(0.0, 1.1, 0.0)
up = util.vec(0.0, 1.0, 0.0)
gGUI.createViewMatrix(eye, target, up)
projMat = util.perspective(50.0, winWidth / winHeight, 0.1, 100.0)

atlas = Texture(ATLAS, flip=False)
pyramid_shader.setUniformVariable(key='ImageTexture', value=atlas, texture=True)
square_shader.setUniformVariable(key='ImageTexture', value=atlas, texture=True)

running = True
while running:
    running = scene.render()
    scene.world.traverse_visit(transUpdate, scene.world.root)
    view = gWindow._myCamera

    axes_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ axes_trans.l2world, mat4=True)
    terrain_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ terrain_trans.l2world, mat4=True)
    for shader, trans in ((pyramid_shader, pyramid_trans), (square_shader, square_trans)):
        shader.setUniformVariable(key='model', value=trans.l2world, mat4=True)
        shader.setUniformVariable(key='View', value=view, mat4=True)
        shader.setUniformVariable(key='Proj', value=projMat, mat4=True)

    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.render_post()

scene.shutdown()
