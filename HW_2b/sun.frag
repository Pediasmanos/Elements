#version 410

in vec2 fragmentTexCoord;
in vec4 pos;

out vec4 outputColor;

uniform float lightIntensity;
uniform sampler2D ImageTexture;

void main()
{
    vec3 sun_color = texture(ImageTexture,fragmentTexCoord).rgb;  //pairnw to current color tou fragment tou hliou

    outputColor = vec4(sun_color*lightIntensity, 1);              //kai apla to fwtizw parapanw me to intensity pou tha tou dwsw
}


// de fwtizetai katholou ara sxedon ola apo to simpletexturephong.frag de xreiazontousan