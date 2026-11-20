"""
Live 2, exercise B -- The planet :: SKELETON

A white planet, lit by a sun (the small yellow ball) with ambient and diffuse light. The shader below
is complete and working. Your job is to make the planet react to how FAR the sun is.

The three places to work are marked TODO 1, TODO 2 and TODO 3, in the fragment shader below. What each
one has to do is described in the exam text. The panel at the top right moves the sun: its distance
from the planet, its direction, and a switch that makes it orbit.

    python live2b_5486.py          (the file name already carries your student number)
"""
import time

import numpy as np

import imgui

import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, RenderMesh
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIDecorator
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.extensions.Shapes import geometry_factory
from Elements.definitions import SHADER_DIR


winWidth = 1200
winHeight = 800

# ==========================================================================================
# THE SHADERS (the places to work are marked TODO 1, TODO 2, TODO 3)
# ==========================================================================================
vertex_shader = """
#version 410

layout (location=0) in vec4 vPosition;
layout (location=1) in vec4 vNormal;

out vec4 pos;
out vec3 normal;

uniform mat4 modelViewProj;
uniform mat4 model;

void main()
{
    gl_Position = modelViewProj * vPosition;
    pos = model * vPosition;                                         // world position
    normal = mat3(transpose(inverse(model))) * vNormal.xyz;          // world normal
}
"""

fragment_shader = """
#version 410

in vec4 pos;
in vec3 normal;

out vec4 outputColor;

uniform vec3 ambientColor;
uniform float ambientStr;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightIntensity;

// ---- the palette
const vec3 WHITE  = vec3(0.95, 0.95, 0.95);
const vec3 BLUE   = vec3(0.10, 0.25, 0.90);
const vec3 GREEN  = vec3(0.20, 0.90, 0.30);
const vec3 RED  = vec3(0.90, 0.20, 0.20);

// ---- the sun is "near" up to NEAR world units from a point, "far" from FAR units on
const float VERY_CLOSE = 1.5;
const float NEAR = 2.5;
const float FAR = 8.0;

void main()
{
    vec3 norm = normalize(normal);
    vec3 lightDir = normalize(lightPos - pos.xyz);

    // ---- TODO 1 ---------------------------------------------------------------------------
    float t;
    float d =  distance(pos.xyz, lightPos);  // distance metaksi tou current shmeiou kai tou hliou
    if(d<= NEAR){
        t = 0.0;
    }else if( d>= FAR){
        t = 1.0;
    }else {
        t = (d - NEAR)/ (FAR- NEAR);      // de xrishmopoihsa tin clamp, kawths mou fainetai pio ksekatharo etsi
    }                                     // episis mou eipe voithos oti den itan ypoxrewtiki h xrisi tis

    // ---- TODO 2 ---------------------------------------------------------------------------
    // Replace the line below.
    vec3 surface;

    if(t<= 0.5){
        if(t == 0.0){
            surface = GREEN;
        }else if(t == 0.5){
          surface = BLUE;
        }else{
            surface = mix(GREEN, BLUE, t/0.5); // apo 0 ews 0.5 ginetai, 0 ews 1
        }
        
    }else{
        if(t == 0.5){
            surface == BLUE;
        }else if( t == 1.0){
            surface == WHITE;
        }else{
            float w;
            if(t == 0.5){
                w = 0.0;
            }else{
                w = clamp(t,0,1);  // apo 0,1 to weight
            }
            surface = mix(BLUE,WHITE, w);
        }
    }

    // Diffuse: 0 on the part that faces away from the sun, 1 where the sun is straight overhead
    float diffuseStr = max(dot(norm, lightDir), 0.0);

    vec3 ambientProduct = ambientStr * ambientColor;
    vec3 diffuseProduct = diffuseStr * lightColor * lightIntensity;

    vec3 color = (ambientProduct + diffuseProduct) * surface;

    // ---- TODO 3 ---------------------------------------------------------------------------
    if(color.g > 0.9 && d < VERY_CLOSE){
        color = RED;     // apla allazw to xrwma tou fragment se red
    }
    
    outputColor = vec4(color, 1);
}
"""

# ==========================================================================================
# THE PLANET: a smooth sphere of radius 1 at the origin, and the sun: a small yellow ball, not lit
# ==========================================================================================
scene = Scene()

# Scenegraph: everything hangs below the root
rootEntity = scene.world.createEntity(Entity(name="RooT"))

initUpdate = scene.world.createSystem(InitGLShaderSystem())
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())

raw_v, raw_i, raw_c = geometry_factory.create_sphere({"lat": 48, "lon": 64, "scale": [2.0, 2.0, 2.0], "color": [0.1, 0.25, 0.9]})
planet_v, planet_i, planet_c, planet_n = geometry_factory.build_smooth_shaded_mesh(raw_v, raw_i, raw_c)

planet = scene.world.createEntity(Entity(name="planet"))
scene.world.addEntityChild(rootEntity, planet)
planet_trans = scene.world.addComponent(planet, BasicTransform(name="planet_trans", trs=util.identity()))
planet_mesh = scene.world.addComponent(planet, RenderMesh(name="planet_mesh"))
planet_mesh.vertex_attributes.append(planet_v)       # attribute 0: vPosition
planet_mesh.vertex_attributes.append(planet_n)       # attribute 1: vNormal
planet_mesh.vertex_index.append(planet_i)
scene.world.addComponent(planet, VertexArray())
planet_shader = scene.world.addComponent(planet, ShaderGLDecorator(
    Shader(vertex_source=vertex_shader, fragment_source=fragment_shader)))

raw_v, raw_i, raw_c = geometry_factory.create_sphere({"lat": 10, "lon": 14, "scale": [0.25, 0.25, 0.25], "color": [1.0, 0.95, 0.2]})
sun = scene.world.createEntity(Entity(name="sun"))
scene.world.addEntityChild(rootEntity, sun)
sun_trans = scene.world.addComponent(sun, BasicTransform(name="sun_trans", trs=util.identity()))
sun_mesh = scene.world.addComponent(sun, RenderMesh(name="sun_mesh"))
sun_mesh.vertex_attributes.append(raw_v)
sun_mesh.vertex_attributes.append(raw_c)
sun_mesh.vertex_index.append(raw_i)
scene.world.addComponent(sun, VertexArray())
sun_shader = scene.world.addComponent(sun, ShaderGLDecorator(
    Shader(vertex_import_file=SHADER_DIR / "ColorMVP.vert", fragment_import_file=SHADER_DIR / "Color.frag")))

# ==========================================================================================
# THE SUN AND THE MATERIAL (the panel changes them)
# ==========================================================================================
state = {
    "distance": 4.0,          # sun to the centre of the planet (the planet has radius 1)
    "azimuth": 55.0,          # degrees around the planet
    "elevation": 20.0,        # degrees above the equator
    "orbit": False,
}

Lambientcolor = util.vec(1.0, 1.0, 1.0)
Lambientstr = 0.12
Lcolor = util.vec(1.0, 1.0, 1.0)
Lintensity = 1.0


def draw_panel():
    imgui.begin("Live 2B - the planet", True)
    _, state["distance"] = imgui.slider_float("sun distance", state["distance"], 1.6, 9.0)
    _, state["azimuth"] = imgui.slider_float("sun azimuth", state["azimuth"], -180.0, 180.0)
    _, state["elevation"] = imgui.slider_float("sun elevation", state["elevation"], -60.0, 60.0)
    _, state["orbit"] = imgui.checkbox("Orbit the sun", state["orbit"])
    imgui.text("Right mouse button + WASD: fly the camera")
    imgui.end()


# ==========================================================================================
# WINDOW, EVENTS, CAMERA
# ==========================================================================================
scene.init(imgui=True, windowWidth=winWidth, windowHeight=winHeight, windowTitle="Elements: Live 2B - the planet", customImGUIdecorator=ImGUIDecorator, openGLversion=4)

# Everything created so far has to be sent to the GPU once (needs the window, i.e. an OpenGL context)
scene.world.traverse_visit(initUpdate, scene.world.root)

gWindow = scene.renderWindow          # the SDL2 window: pixels, mouse, keyboard, and the camera matrix
gGUI = scene.gContext                 # the ImGui layer around it, which also owns the camera

# Camera: where we stand (eye), what we look at (target), which way is up
eye = util.vec(0.0, 1.0, 5.5)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
gGUI.createViewMatrix(eye, target, up)                  # sets the camera (the mouse and the GUI move it from here)
projMat = util.perspective(50.0, winWidth / winHeight, 0.1, 100.0)

start_time = time.time()

# ==========================================================================================
# MAIN LOOP
# ==========================================================================================
running = True
while running:
    running = scene.render()                                          # window, events
    draw_panel()

    t = time.time() - start_time
    view = gWindow._myCamera                                          # the mouse and the GUI both write here
    if state["orbit"]:
        state["azimuth"] = (state["azimuth"] + 0.5 + 180.0) % 360.0 - 180.0
    az, el = np.radians(state["azimuth"]), np.radians(state["elevation"])
    sunPosition = state["distance"] * np.array([np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)])

    sun_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ util.translate(*sunPosition), mat4=True)

    planet_shader.setUniformVariable(key='modelViewProj', value=projMat @ view @ planet_trans.l2world, mat4=True)
    planet_shader.setUniformVariable(key='model', value=planet_trans.l2world, mat4=True)
    planet_shader.setUniformVariable(key='ambientColor', value=Lambientcolor, float3=True)
    planet_shader.setUniformVariable(key='ambientStr', value=Lambientstr, float1=True)
    planet_shader.setUniformVariable(key='lightPos', value=util.vec(*sunPosition), float3=True)
    planet_shader.setUniformVariable(key='lightColor', value=Lcolor, float3=True)
    planet_shader.setUniformVariable(key='lightIntensity', value=Lintensity, float1=True)

    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.render_post()

scene.shutdown()
