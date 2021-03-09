varying highp vec4 var_position;
varying mediump vec3 var_normal;
varying mediump vec2 var_texcoord0;
varying highp vec4 var_color0;
varying mediump vec4 var_light;

uniform lowp sampler2D tex0;

void main()
{
    // Pre-multiply alpha since all runtime textures already are
    vec4 color = texture2D(tex0, var_texcoord0.xy);

    // Diffuse light calculations
    vec3 ambient_light = vec3(0.1);
    vec3 diff_light = vec3(normalize(var_light.xyz - var_position.xyz));
    diff_light = max(dot(var_normal,diff_light), 0.0) + ambient_light;
    diff_light = clamp(diff_light, 0.0, 1.0);

    gl_FragColor = vec4(color.rgb*diff_light*var_color0.rgb,1.0);
}
