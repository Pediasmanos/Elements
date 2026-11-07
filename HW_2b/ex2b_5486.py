import os
import random
import numpy as np

from Elements.definitions import SHADER_DIR, TEXTURE_DIR, SKYBOX_DIR
import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, Camera, RenderMesh
from Elements.pyECSS.System import TransformSystem, CameraSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.Viewer import RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator2
import imgui

from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.extensions.UV_Mapping.Gui import UVGui

from OpenGL.GL import GL_LINES
import OpenGL.GL as gl

import Elements.utils.normals as norm
from Elements.utils.terrain import generateTerrain
from Elements.utils.obj_to_mesh import obj_to_mesh

from Elements.utils.Shortcuts import displayGUI_text
from Elements.extensions.UV_Mapping.ObjectGenerator import UVObjectGenerator
from Elements.pyGLV.GL.Textures import Texture, get_texture_faces
from pathlib import Path
import time



#from Elements.extensions.UV_Mapping.TextureMapping import TextureGUI
example_description = \
"This is the first examples that demonstrates the usage of the Camera System \n\
instead of the use of the lookAt function to create the view matrix. \n\
You may move the camera using the mouse or the Scenegraph. \n\n\
NOTE: To change any TRS via the ECSS GUI, only this TRS must be toggled on!\n\n\
You may see the ECS Scenegraph showing Entities & Components of the scene and \n\
various information about them. Hit ESC OR Close the window to quit." 

#Light
#Lposition = util.vec(5.0, 2.0, 2.0) #uniform lightpos                #o hlios einai to neo light source
Lambientcolor = util.vec(1.0, 1.0, 1.0) #uniform ambient color
Lambientstr = 0.3 #uniform ambientStr
#LviewPos = util.vec(2.5, 2.8, 5.0) #uniform viewpos
Lcolor = util.vec(1.0,1.0,1.0)
#Lintensity = 0.8
#Material
Mshininess = 0.4 
Mcolor = util.vec(0.8, 0.0, 0.8)

winWidth = 1200
winHeight = 800

scene = Scene()    

# Scenegraph with Entities, Components
rootEntity = scene.world.createEntity(Entity(name="RooT"))
entityCam1 = scene.world.createEntity(Entity(name="Entity1"))
scene.world.addEntityChild(rootEntity, entityCam1)
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="Entity1_TRS", trs=util.translate(0,0,-8)))

eye = util.vec(0.0, 14.0, 22.0)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
 
projMat = util.perspective(50.0, winWidth/winHeight, 0.01, 100.0)  

m = np.linalg.inv(projMat @ view)



skybox = scene.world.createEntity(Entity(name="Skybox"))
scene.world.addEntityChild(rootEntity, skybox)
transSkybox = scene.world.addComponent(skybox, BasicTransform(name="transSkybox", trs=util.identity())) #util.identity()
meshSkybox = scene.world.addComponent(skybox, RenderMesh(name="meshSkybox"))

#BASIC CUBE FOR THE SKYBOX
minbox = -50
maxbox = 50
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


entityCam2 = scene.world.createEntity(Entity(name="Entity_Camera"))
scene.world.addEntityChild(entityCam1, entityCam2)
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="Camera_TRS", trs=util.identity()))
# orthoCam = scene.world.addComponent(entityCam2, Camera(util.ortho(-100.0, 100.0, -100.0, 100.0, 1.0, 100.0), "orthoCam","Camera","500"))
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))


# Systems
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())



# Generate skybox cube
vertexSkybox, indexSkybox, _ = norm.generateUniqueVertices(vertexSkybox,indexSkybox)

meshSkybox.vertex_attributes.append(vertexSkybox)
meshSkybox.vertex_index.append(indexSkybox)
vArraySkybox = scene.world.addComponent(skybox, VertexArray())
shaderSkybox = scene.world.addComponent(skybox, ShaderGLDecorator(Shader(vertex_import_file = SHADER_DIR / "StaticSkybox.vert", fragment_import_file=SHADER_DIR / "StaticSkybox.frag")))

def fix_sphere_uvs(body, sectorCount=32, stackCount=16):
    uvs = []

    for i in range(stackCount + 1):
        for j in range(sectorCount + 1):
            uvs.append([
                1.0 - j / sectorCount,
                i / stackCount
            ])

    body.mesh.vertex_attributes[2] = np.array(
        uvs, dtype=np.float32
    )

sun = UVObjectGenerator.Sphere(name=f"sun", radius=1.0)  # se ola radius=1.0 afou sto objectGenerator.py ta arxikopoiei me radius=0.5 pou xalaei ta sizes
scene.world.addEntityChild(rootEntity, sun)
sun.trans.trs = util.scale(1.5, 1.5, 1.5)
#--------------------------------------------
t = 0  # arxi xronou

theta = 2 * np.pi*t /20
earth_x = 6 * np.cos(theta) - 3.317
earth_z = 5 * np.sin(theta)
earth_y = 0.2* earth_z

earth_position = scene.world.createEntity(Entity(name="earth_position"))
scene.world.addEntityChild(rootEntity,earth_position)
earth_position_trs = scene.world.addComponent(earth_position, BasicTransform(name="earth_position_trs", trs=util.translate(earth_x, earth_y, earth_z)))
#--------------------------------------------
e_rotation_angle = 360*t /2
earth_angle = scene.world.createEntity(Entity(name="earth_angle"))
scene.world.addEntityChild(earth_position,earth_angle)
earth_angle_trs = scene.world.addComponent(earth_angle,BasicTransform(name="earth_angle_trs", trs=util.rotate((1,0,0), 23.4) @ util.rotate((0,1,0), e_rotation_angle)))

earth = UVObjectGenerator.Sphere(name="earth", radius=1.0)
scene.world.addEntityChild(earth_angle, earth)
earth.trans.trs = util.scale(0.45, 0.45, 0.45)

phi = 2*np.pi*t/5
moon_x = 1.1*np.cos(phi)
moon_z = 1.1*np.sin(phi)

moon_position = scene.world.createEntity(Entity(name="moon_position"))
scene.world.addEntityChild(earth_position,moon_position)
moon_position_trs = scene.world.addComponent(moon_position, BasicTransform(name="moon_position_trs", trs=util.translate(moon_x, 0.0 ,moon_z) @util.rotate((0, 1, 0), -np.degrees(phi))))

moon = UVObjectGenerator.Sphere(name="moon", radius=1.0)
scene.world.addEntityChild(moon_position, moon)
moon.trans.trs = util.scale(0.12, 0.12, 0.12)
#--------------------------------------------

psi = -2* np.pi *t/45
ice_x = 11*np.cos(psi) -4.583
ice_z = 10* np.sin(psi)
ice_y = 0.15*ice_z

ice_planet_position = scene.world.createEntity(Entity(name="ice_planet_position"))
scene.world.addEntityChild(rootEntity,ice_planet_position)
ice_planet_trs = scene.world.addComponent(ice_planet_position, BasicTransform(name="ice_planet_position_trs", trs=util.translate(ice_x, ice_y, ice_z)))

ice_planet = UVObjectGenerator.Sphere(name="ice_planet",radius=1.0)
scene.world.addEntityChild(ice_planet_position, ice_planet)
ice_planet.trans.trs = util.scale(0.8,0.8,0.8)

fix_sphere_uvs(sun)
fix_sphere_uvs(earth)
fix_sphere_uvs(moon)
fix_sphere_uvs(ice_planet)

shader_folder = Path(__file__).resolve().parent
earth.shaderDec.component.vertex_source = (shader_folder / "planet_STP.vert").read_text()    # kanw override ta shader source codes me ta 
earth.shaderDec.component.fragment_source = (shader_folder / "planet_STP.frag").read_text()  #  dika mou, xrisimopoiwntas ta arxika shader components
                                                                                             #  kratwntas etsi ta meshes opws htan
moon.shaderDec.component.vertex_source = (shader_folder / "planet_STP.vert").read_text()
moon.shaderDec.component.fragment_source = (shader_folder / "planet_STP.frag").read_text()

sun.shaderDec.component.vertex_source = (shader_folder / "sun.vert").read_text()
sun.shaderDec.component.fragment_source = (shader_folder / "sun.frag").read_text()

ice_planet.shaderDec.component.vertex_source = (shader_folder / "ice.vert").read_text()
ice_planet.shaderDec.component.fragment_source = (shader_folder / "ice.frag").read_text()


running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "Elements: Let There Be Light", openGLversion = 4, customImGUIdecorator = ImGUIecssDecorator2)

# pre-pass scenegraph to initialise all GL context dependent geometry, shader classes
# needs an active GL context
scene.world.traverse_visit(initUpdate, scene.world.root)

################### EVENT MANAGER ###################

eManager = scene.world.eventManager
gWindow = scene.renderWindow
gGUI = scene.gContext

renderGLEventActuator = RenderGLStateSystem()


eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow 
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator


eye = util.vec(0.0, 14.0, 22.0)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
# projMat = util.ortho(-10.0, 10.0, -10.0, 10.0, -1.0, 10.0)  
# projMat = util.perspective(90.0, 1.33, 0.1, 100)  
projMat = util.perspective(50.0, winWidth/winHeight, 0.01, 100.0)   

#gWindow._myCamera = view # otherwise, an imgui slider must be moved to properly update
scene.gContext.createViewMatrix(eye, target, up)

# Any folder under SKYBOX_DIR works -- Cloudy, Day_Sunless, Sea, Stars.
skybox_texture_locations = SKYBOX_DIR / "skybox_ex2"
front_img = skybox_texture_locations / "front.png"
right_img = skybox_texture_locations / "right.png"
left_img = skybox_texture_locations / "left.png"
back_img = skybox_texture_locations / "back.png"
bottom_img = skybox_texture_locations / "bottom.png"
top_img = skybox_texture_locations / "top.png"


face_data = get_texture_faces(front_img,back_img,top_img,bottom_img,left_img,right_img)

shaderSkybox.setUniformVariable(key='cubemap', value=face_data, texture3D=True)


#LOAD THE TEXTURE AFTER THE OPENGL CONTEXT IS CREATED!!!!
texturePath1 = TEXTURE_DIR / "sun.jpg"
texturePath2 = TEXTURE_DIR / "earth.jpg"
texturePath3 = TEXTURE_DIR / "moon.jpg"

texture1 = Texture(texturePath1)
texture2 = Texture(texturePath2)
texture3 = Texture(texturePath3)

sun.shaderDec.setUniformVariable(key='ImageTexture', value=texture1, texture=True)
earth.shaderDec.setUniformVariable(key='ImageTexture', value=texture2, texture=True)
moon.shaderDec.setUniformVariable(key='ImageTexture', value=texture3, texture=True)
ice_planet.shaderDec.setUniformVariable(key='ImageTexture', value=texture2, texture=True)

##############################################################
##DONE NOW THE TEXTURE IS READY TO BE USED IN THE SHADER ACCORDING TO THE UVS OF THE OBJECT##########
def uniform_setter(given_shader, given_trs):
    given_shader.setUniformVariable(key='model', value=given_trs.l2world, mat4=True)
    given_shader.setUniformVariable(key='View', value=view, mat4=True)
    given_shader.setUniformVariable(key='Proj', value=projMat, mat4=True)
    given_shader.setUniformVariable(key='ambientColor',value=Lambientcolor,float3=True)
    given_shader.setUniformVariable(key='ambientStr',value=Lambientstr,float1=True)
    given_shader.setUniformVariable(key='viewPos',value=LviewPos,float3=True)
    given_shader.setUniformVariable(key='lightPos',value=Lposition,float3=True)
    given_shader.setUniformVariable(key='lightColor',value=Lcolor,float3=True)
    given_shader.setUniformVariable(key='lightIntensity',value=Lintensity,float1=True)
    given_shader.setUniformVariable(key='shininess',value=Mshininess,float1=True)

start_time = time.time()
while running:
    running = scene.render()
    t = time.time() - start_time
    displayGUI_text(example_description)
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam)
    scene.world.traverse_visit(camUpdate, scene.world.root)
    
    theta = 2 * np.pi*t /20
    phi = 2*np.pi*t/5
    psi = -2* np.pi *t/45
    earth_x = 6 * np.cos(theta) - 3.317
    earth_z = 5 * np.sin(theta)
    earth_y = 0.2* earth_z
    moon_x = 1.1*np.cos(phi)
    moon_z = 1.1*np.sin(phi)
    ice_x = 11*np.cos(psi) -4.583
    ice_z = 10* np.sin(psi)
    ice_y = 0.15*ice_z
    e_rotation_angle = 360*t /2

    
    earth_position_trs.trs = util.translate(earth_x,earth_y,earth_z)
    earth_angle_trs.trs = util.rotate((1,0,0), 23.4) @ util.rotate((0,1,0), e_rotation_angle)
    
    moon_position_trs.trs = util.translate(moon_x, 0.0, moon_z) @ util.rotate((0, 1, 0), -np.degrees(phi))
    
    ice_planet_trs.trs = util.translate(ice_x, ice_y, ice_z)

    scene.world.traverse_visit(transUpdate, scene.world.root)

    view =  gWindow._myCamera 
    LviewPos = gWindow._cameraEye
    Lposition = sun.trans.l2world[:3, 3].copy()
    Lintensity = 1.0 * (1 + 0.4*np.sin(2*np.pi *t/8))
    
    uniform_setter(sun.shaderDec, sun.trans)
    uniform_setter(earth.shaderDec, earth.trans)
    uniform_setter(moon.shaderDec, moon.trans)
    uniform_setter(ice_planet.shaderDec, ice_planet.trans)

    shaderSkybox.setUniformVariable(key='Proj', value=projMat, mat4=True)
    shaderSkybox.setUniformVariable(key='View', value=view, mat4=True)

    scene.world.traverse_visit(renderUpdate, scene.world.root) 
    scene.render_post()
    
scene.shutdown()