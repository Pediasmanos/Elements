#version 410

layout (location=0) in vec4 vPos;
layout (location=1) in vec4 vNormal;

out vec4 pos;
out vec3 normal;
out float k;
out vec3 objectPosition;

uniform mat4 model;
uniform mat4 View;
uniform mat4 Proj;
uniform vec3 lightPos;

void main()
{   
    vec3 planet_center = (model * vec4(0.0, 0.0, 0.0, 1.0)).xyz; 

    float d = length(planet_center - lightPos);
    float d_s = d - 1.5;

    k = clamp((d_s -4.5)/10, 0, 1);
    float s = 0.6 + 0.8*k;

    objectPosition = vPos.xyz;
    vec4 scaled_pos = vec4(vPos.xyz * s, 1.0);

    gl_Position =  Proj * View * model * scaled_pos;
    pos = model * scaled_pos;
    normal = mat3(transpose(inverse(model))) * vNormal.xyz;
}
