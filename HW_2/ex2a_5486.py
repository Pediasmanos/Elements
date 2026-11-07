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

from OpenGL.GL import GL_LINES
import imgui

import Elements.utils.normals as norm
from Elements.pyGLV.GL.Textures import Texture
from Elements.utils.terrain import generateTerrain

from Elements.definitions import TEXTURE_DIR, SHADER_DIR, SKYBOX_DIR
from Elements.pyGLV.GL.Textures import get_texture_faces


#Light
Lposition = util.vec(3.0, 2.0, 5.0)
Lintensity = 1.0
Lambientstr = 0.2

Lambientcolor = util.vec(1.0, 1.0, 1.0) #uniform ambient color
Lcolor = util.vec(1.0,1.0,1.0)
Mshininess = 0.4 # how strong the specular highlight is
MspecularExponent = 32.0


winWidth = 1200
winHeight = 800
scene = Scene()

rootEntity = scene.world.createEntity(Entity(name="RooT"))

transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())

#-----------------------------------------------------------------------------------------------------------
"""
vertexAxes = np.array([
    [0.0, 0.0, 0.0, 1.0],
    [1.5, 0.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 1.5, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 1.5, 1.0]
],dtype=np.float32) 
colorAxes = np.array([
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
indexAxes = np.array((0,1,2,3,4,5), np.uint32)

# axes
axes = scene.world.createEntity(Entity(name="axes"))
scene.world.addEntityChild(rootEntity, axes)
axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.001, 0.0)))
axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))
axes_mesh.vertex_attributes.append(vertexAxes)
axes_mesh.vertex_attributes.append(colorAxes)
axes_mesh.vertex_index.append(indexAxes)
axes_vArray = scene.world.addComponent(axes, VertexArray(primitive=GL_LINES)) # note the primitive change
axes_shader = scene.world.addComponent(axes, ShaderGLDecorator(Shader(vertex_import_file=SHADER_DIR / "ColorMVP.vert", fragment_import_file=SHADER_DIR / "Color.frag")))
"""
#======================================
floor_vert = np.array([
    [-10.0, 0.0, 10.0, 1.0],  #0
    [10.0, 0.0, 10.0, 1.0],   #1
    [10.0, 0.0, -10, 1.0],    #2
    [-10.0, 0.0, -10.0, 1.0]  #3
], dtype=np.float32)

floor_ind = np.array((1,3,0, 1,2,3), np.uint32)
floor_vertices, floor_indices, _, floor_normals = norm.generateFlatNormalsMesh(floor_vert , floor_ind)

floor_uv = np.array([
    [10.0, 0.0],   # 1
    [0.0, 10.0],   # 3
    [0.0, 0.0],    # 0

    [10.0, 0.0],   # 1
    [10.0, 10.0],  # 2
    [0.0, 10.0]    # 3
], dtype=np.float32)

floor = scene.world.createEntity(Entity(name="floor"))
scene.world.addEntityChild(rootEntity, floor)
floor_trs = scene.world.addComponent(floor, BasicTransform(name="cube2_trans", trs=util.translate(0,0,0) ))
floor_mesh = scene.world.addComponent(floor, RenderMesh(name="cube2_mesh"))
floor_mesh.vertex_attributes.append(floor_vertices)
floor_mesh.vertex_attributes.append(floor_normals)
floor_mesh.vertex_attributes.append(floor_uv)
floor_mesh.vertex_index.append(floor_indices)
floor_vertexArray = scene.world.addComponent(floor, VertexArray())
floor_shader = scene.world.addComponent(floor, ShaderGLDecorator(Shader(vertex_import_file=SHADER_DIR / "SimpleTexturePhong.vert", fragment_import_file=SHADER_DIR / "SimpleTexturePhong.frag")))


#======================================
skybox = scene.world.createEntity(Entity(name="Skybox"))
scene.world.addEntityChild(rootEntity, skybox)
transSkybox = scene.world.addComponent(skybox, BasicTransform(name="transSkybox", trs=util.identity()))
meshSkybox = scene.world.addComponent(skybox, RenderMesh(name="meshSkybox"))

minbox = -30
maxbox = 30
vertexSkybox = np.array([
    [minbox, minbox, maxbox, 1.0],
    [minbox, maxbox, maxbox, 1.0],
    [maxbox, maxbox, maxbox, 1.0],
    [maxbox, minbox, maxbox, 1.0], 
    [minbox, minbox, minbox, 1.0], 
    [minbox, maxbox, minbox, 1.0], 
    [maxbox, maxbox, minbox, 1.0], 
    [maxbox, minbox, minbox, 1.0]
],dtype=np.float32)

#index array for Skybox
indexSkybox = np.array((1,0,3, 1,3,2, 
                  2,3,7, 2,7,6,
                  3,0,4, 3,4,7,
                  6,5,1, 6,1,2,
                  4,5,6, 4,6,7,
                  5,4,0, 5,0,1), np.uint32) 

vertexSkybox, indexSkybox, _ = norm.generateUniqueVertices(vertexSkybox,indexSkybox)

meshSkybox.vertex_attributes.append(vertexSkybox)
meshSkybox.vertex_index.append(indexSkybox)
vArraySkybox = scene.world.addComponent(skybox, VertexArray())
shaderSkybox = scene.world.addComponent(skybox, ShaderGLDecorator(Shader(vertex_import_file=SHADER_DIR / "StaticSkybox.vert", fragment_import_file=SHADER_DIR / "StaticSkybox.frag")))

#======================================
cube_vertices = np.array([
    [-1.0, -1.0, 1.0, 1.0],
    [-1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, -1.0, 1.0, 1.0], 
    [-1.0, -1.0, -1.0, 1.0], 
    [-1.0, 1.0, -1.0, 1.0], 
    [1.0, 1.0, -1.0, 1.0], 
    [1.0, -1.0, -1.0, 1.0]
],dtype=np.float32)

cube_faces = {
    "front" :[1,0,3,2],
    "right" :[2,3,7,6],
    "back"  :[6,7,4,5],
    "left"  :[5,4,0,1],
    "top"   :[2,6,5,1],
    "bottom":[3,0,4,7]
}

face_indices = np.array([             #p.x sto front tha ginei  trinagle1: 1,0,3  kai triangle2: 1,3,2
    0, 1, 2,
    0, 2, 3
], dtype=np.uint32)

face_uvs = {
    "front": np.array([
        [0, 0], [1, 0], [1, 1], [0, 1]
    ], dtype=np.float32),

    "back": np.array([
        [1, 1], [0, 1], [0, 0], [1, 0]
    ], dtype=np.float32),

    "left": np.array([
        [0, 0], [1, 0], [1, 1], [0, 1]
    ], dtype=np.float32),

    "right": np.array([
        [1, 1], [0, 1], [0, 0], [1, 0]
    ], dtype=np.float32),

    "top": np.array([
        [0, 1], [0, 0], [1, 0], [1, 1]
    ], dtype=np.float32),

    "bottom": np.array([
        [1, 1], [0, 1], [0, 0], [1, 0]
    ], dtype=np.float32)
}

cube = scene.world.createEntity(Entity(name="cube"))
scene.world.addEntityChild(rootEntity, cube)
cube_trs = scene.world.addComponent(cube, BasicTransform(name="cube_trans", trs=util.translate(0.0, np.sqrt(3), 0.0)@ util.rotate((-1, 0, 1), np.degrees(np.arctan(np.sqrt(2))))))


cube_faces_info = {}
def draw_cube_face(f_name):
    current_vertices = cube_vertices[cube_faces[f_name]]
    
    vertices, indices, _, normals = norm.generateFlatNormalsMesh(current_vertices , face_indices)
    face = scene.world.createEntity(Entity(name= f_name))
    scene.world.addEntityChild(cube, face)
    face_trs = scene.world.addComponent(face, BasicTransform(name= f_name +"_trans", trs=util.identity() ))
    face_mesh = scene.world.addComponent(face, RenderMesh(name= f_name+ "_mesh"))
    face_mesh.vertex_attributes.append(vertices)
    face_mesh.vertex_attributes.append(normals)
    face_mesh.vertex_attributes.append(face_uvs[f_name][face_indices])
    face_mesh.vertex_index.append(indices)
    face_vertexArray = scene.world.addComponent(face, VertexArray())
    face_shader = scene.world.addComponent(face, ShaderGLDecorator(Shader(vertex_import_file=SHADER_DIR / "SimpleTexturePhong.vert", fragment_import_file=SHADER_DIR / "SimpleTexturePhong.frag")))
    cube_faces_info[f_name] = (face_shader, face_trs)

draw_cube_face("front")
draw_cube_face("right")
draw_cube_face("back")
draw_cube_face("left")
draw_cube_face("top")
draw_cube_face("bottom")

#-----------------------------------------------------------------------------------------------------------
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "ex2a_5486", openGLversion = 4, customImGUIdecorator = ImGUIecssDecorator2)
scene.world.traverse_visit(initUpdate, scene.world.root)


def uniform_setter(given_shader, given_trs):
    given_shader.setUniformVariable(key='model', value=given_trs.l2world, mat4=True)
    given_shader.setUniformVariable(key='View', value=view, mat4=True)
    given_shader.setUniformVariable(key='Proj', value=projMat, mat4=True)
    given_shader.setUniformVariable(key='ambientColor',value=Lambientcolor,float3=True)
    given_shader.setUniformVariable(key='ambientStr',value=Lambientstr,float1=True)
    given_shader.setUniformVariable(key='viewPos',value=viewPos,float3=True)
    given_shader.setUniformVariable(key='lightPos',value=Lposition,float3=True)
    given_shader.setUniformVariable(key='lightColor',value=Lcolor,float3=True)
    given_shader.setUniformVariable(key='lightIntensity',value=Lintensity,float1=True)
    given_shader.setUniformVariable(key='shininess',value=Mshininess,float1=True)
    given_shader.setUniformVariable(key='specularExponent',value=MspecularExponent,float1=True)

QtexturePath = TEXTURE_DIR / "face_Q.png"
TWOtexturePath = TEXTURE_DIR / "face_2.png"
FtexturePath = TEXTURE_DIR / "face_F.png"
GtexturePath = TEXTURE_DIR / "face_G.png"
JtexturePath = TEXTURE_DIR / "face_J.png"
PtexturePath = TEXTURE_DIR / "face_P.png"

textureQ = Texture(QtexturePath)
texture2 = Texture(TWOtexturePath)
textureF = Texture(FtexturePath)
textureG = Texture(GtexturePath)
textureJ = Texture(JtexturePath)
textureP = Texture(PtexturePath)

cube_faces_info["front"][0].setUniformVariable(key='ImageTexture', value=textureQ, texture=True)
cube_faces_info["right"][0].setUniformVariable(key='ImageTexture', value=textureF, texture=True)
cube_faces_info["back"][0].setUniformVariable(key='ImageTexture', value=texture2, texture=True)
cube_faces_info["left"][0].setUniformVariable(key='ImageTexture', value=textureG, texture=True)
cube_faces_info["top"][0].setUniformVariable(key='ImageTexture', value=textureJ, texture=True)
cube_faces_info["bottom"][0].setUniformVariable(key='ImageTexture', value=textureP, texture=True)

texturePath1 = TEXTURE_DIR / "checker.png"
texture1 = Texture(texturePath1)
floor_shader.setUniformVariable(key='ImageTexture', value=texture1, texture=True)


#===== sky box ====================
skybox_texture_locations = SKYBOX_DIR / "skybox_ex1"
front_img = skybox_texture_locations / "front.png"
right_img = skybox_texture_locations / "right.png"
left_img = skybox_texture_locations / "left.png"
back_img = skybox_texture_locations / "back.png"
bottom_img = skybox_texture_locations / "bottom.png"
top_img = skybox_texture_locations / "top.png"

face_data = get_texture_faces(front_img,back_img,top_img,bottom_img,left_img,right_img)
shaderSkybox.setUniformVariable(key='cubemap', value=face_data, texture3D=True)
#==================================

gWindow = scene.renderWindow
gGUI = scene.gContext

eye = util.vec(0.0, 2.5, 6.0)
target = util.vec(0.0, 1.2, 0.0)
up = util.vec(0.0, 1.0, 0.0)
gGUI.createViewMatrix(eye, target, up)
projMat = util.perspective(50.0, winWidth/winHeight, 0.01, 100.0)


Pause = False
speed = 45.0
light_x = 3.0
light_y = 2.0
light_z = 5.0

angle = -21
lowest_y = min((cube_trs.trs @ vertex)[1] for vertex in cube_vertices)

running = True
prev_time = time.time()
while running:
    running = scene.render()
    
    curr_time = time.time()
    dt = curr_time - prev_time
    prev_time = curr_time
    
    imgui.set_next_window_position(winWidth - 320, 20, imgui.FIRST_USE_EVER)
    imgui.set_next_window_size(500, 300, imgui.FIRST_USE_EVER)
    imgui.begin("Photo cube")
    _, Pause = imgui.checkbox("Pause", Pause)
    _, speed = imgui.slider_float("Spin speed (deg/s)", speed,-180.0, 180.0)
    _, light_x = imgui.slider_float("Light x", light_x,-10.0, 10.0)
    _, light_y = imgui.slider_float("Light y", light_y, 0.5, 12.0)
    _, light_z = imgui.slider_float("Light z", light_z,-10.0, 10.0)
    Lposition = util.vec(light_x, light_y, light_z)
    
    imgui.text(f"Lowest vertex y = {lowest_y:+.6f}")
    imgui.end()
    
    if not Pause:
        angle = angle + speed*dt

    cube_trs.trs = (util.translate(0.0, np.sqrt(3), 0.0)@ util.rotate((0, 1, 0), angle)@ util.rotate((-1, 0, 1), np.degrees(np.arctan(np.sqrt(2)))))
    lowest_y = min((cube_trs.trs @ vertex)[1] for vertex in cube_vertices)
    
    scene.world.traverse_visit(transUpdate, scene.world.root)
    view = gWindow._myCamera  
    viewPos = gWindow._cameraEye
    
    #axes_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ axes_trans.l2world, mat4=True)
    
    uniform_setter(cube_faces_info["front"][0], cube_faces_info["front"][1])
    uniform_setter(cube_faces_info["right"][0], cube_faces_info["right"][1])
    uniform_setter(cube_faces_info["back"][0], cube_faces_info["back"][1])
    uniform_setter(cube_faces_info["left"][0], cube_faces_info["left"][1])
    uniform_setter(cube_faces_info["top"][0], cube_faces_info["top"][1])
    uniform_setter(cube_faces_info["bottom"][0], cube_faces_info["bottom"][1])
    
    uniform_setter(floor_shader, floor_trs)
    
    shaderSkybox.setUniformVariable(key='Proj', value=projMat, mat4=True)
    shaderSkybox.setUniformVariable(key='View', value=view, mat4=True)
    
    
    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.render_post()

scene.shutdown()
