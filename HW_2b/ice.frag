#version 410

in vec4 pos;
in vec3 normal;
in float k;
in vec3 objectPosition;

out vec4 outputColor;

// Phong products
uniform vec3 ambientColor;
uniform float ambientStr;

// Lighting 
uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightIntensity;

// Material
uniform float shininess;
//: How *tight* the specular highlight is (shininess, above, is how *strong* it is). Bigger means
//: a smaller, sharper highlight. Left unset it falls back to 32.0, the value this shader used to
//: hard-code, so code written before this was a uniform keeps rendering exactly as it did.
uniform float specularExponent;

float hash(vec3 p){
    p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
    p = p *17;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float noise(vec3 x){
    vec3 i = floor(x);
    vec3 f = fract(x);

    f = f * f *(3 - 2*f);

    float corner_000 = hash(i + vec3(0, 0, 0));
    float corner_001 = hash(i + vec3(0, 0, 1));  // 8 corners of the cell
    float corner_010 = hash(i + vec3(0, 1, 0));
    float corner_011 = hash(i + vec3(0, 1, 1));
    float corner_100 = hash(i + vec3(1, 0, 0));
    float corner_101 = hash(i + vec3(1, 0, 1)); 
    float corner_110 = hash(i + vec3(1, 1, 0));
    float corner_111 = hash(i + vec3(1, 1, 1));            

    float m1 = mix(corner_000,corner_001,f.z);
    float m2 = mix(corner_010, corner_011, f.z);  
    float m3 = mix(corner_100, corner_101, f.z); // prwta kanw interpolate me vasi to z
    float m4 = mix(corner_110, corner_111, f.z); // (epilegw zeugaria pou exoun mono diafora sto z)

    float m13 = mix(m1,m3,f.x);
    float m24 = mix(m2,m4,f.x);      // interpolate me vasi to x (mono diafora sto x)

    float final_mix = mix(m13,m24, f.y); // interpolate me to y
    return final_mix;
}

float fbm(vec3 p){
    float v = 0, a = 0.5;
    for(int i=0; i<3; i++){
        v = v + a* noise(p);
        p = p * 2; 
        a = a * 0.5;
    }
    return v;
}

void main()
{
    float n = fbm(objectPosition * 8);
    float veins = 1 - smoothstep(0.0,0.05, abs(n-0.42));
    float frost = 0.88 + 0.12 * noise(objectPosition * 30);
    float shade = frost * (1 - 0.45 *veins);

    vec3 green = vec3(0.30,0.85,0.25);
    vec3 white = vec3(1.0, 1.0, 1.0);
    vec3 tint = mix(green, white, k);
    vec3 color = shade * tint;

    vec3 norm = normalize(normal);
    vec3 lightDir = normalize(lightPos - pos.xyz);

    float d = length(lightPos - pos.xyz);
    float attenuation = 1 / (1+ 0.02*d + 0.005*d*d);   // gia to part B 

    vec3 viewDir = normalize(viewPos - pos.xyz);
    vec3 reflectDir = reflect(-lightDir, norm);

    // Ambient
    vec3 ambientProduct = ambientStr * ambientColor;
    // Diffuse
    float diffuseStr = max(dot(norm, lightDir), 0.0);
    vec3 diffuseProduct = diffuseStr * lightColor;
    // Specular
    float specExp = specularExponent > 0.0 ? specularExponent : 32.0;
    float specularStr = pow(max(dot(viewDir, reflectDir), 0.0), specExp);


    // No highlight on a face turned away from the light.
    float facingLight = step(0.0, dot(norm, lightDir));
    vec3 specularProduct = facingLight * shininess * specularStr * lightColor;

    // The texture colours the ambient/diffuse terms only; the specular keeps the light's colour,
    // so a textured surface still gets a white highlight. Same composition as Phong.frag.
    vec3 result = (ambientProduct + diffuseProduct * lightIntensity * attenuation) * color  // prosthiki tou attenuation kai edw kai tou color
                + specularProduct * lightIntensity * attenuation;
    outputColor = vec4(result, 1);
}
