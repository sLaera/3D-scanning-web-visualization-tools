Shader "Custom/Heatmap"
{
    Properties
    {
        _PointsTex ("Base (RGB)", 2D) = "gray" {}
        _Positions ("Positions", 2D) = "white" {}
        _RadiusSearch ("_RadiusSearch", Int) = 25
        _ColorMult ("Color multiplier", Color) = (1,1,1,.5)
        [Toggle] _Invert_colors ("Invert colors", Int) = 0

        _WorldColor ("WorldColor", Color) = (0.35,0.35,0.35,.5)

        _OutlineWidth ("Outline Width", Range(0, 10)) = 1
        _OutlineColor ("Outline Color", Color) = (0, 0, 0, 1)
    }
    SubShader
    {
        Tags
        {
            "Queue" = "Overlay" "RenderType" = "Opaque"
        }

        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            //            ZWrite Off
            Fog
            {
                Mode Off
            }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma geometry geom
            #include "UnityCG.cginc"

            sampler2D _PointsTex;
            sampler2D _Positions;
            float4    _PointsTex_TexelSize;
            // float4    _Positions_TexelSize;
            int _RadiusSearch;

            fixed4 _WorldColor;

            fixed4 _ColorMult;
            int    _Invert_colors;

            struct v2g {
                float2 uv : TEXCOORD0;
                float4 vertex : POSITION;
                half4  color : COLOR0;
                float3 normal : NORMAL;
            };

            v2g vert(appdata_full v)
            {
                v2g o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord;
                o.color = v.color;
                o.normal = v.normal;
                return o;
            }

            struct g2f {
                float2 uv : TEXCOORD0;
                float4 vertex : POSITION;
                float2 uvV1 : TEXCOORD1; // fist vertex of the triangle face
                float2 uvV2 : TEXCOORD2; // second vertex of the triangle face
                float2 uvV3 : TEXCOORD3; // third vertex of the triangle face
                half4  color : COLOR0;
                float3 normal : NORMAL;
            };

            [maxvertexcount(3)]
            void geom(triangle v2g IN[3], inout TriangleStream<g2f> tristream)
            {
                g2f o;
                for(int i = 0; i < 3; i++)
                {
                    //IN[i].worldPos
                    //IN[i].uv;
                    o.vertex = IN[i].vertex;
                    o.uv = IN[i].uv;
                    o.normal = IN[i].normal;

                    o.uvV1 = IN[0].uv;
                    o.uvV2 = IN[1].uv;
                    o.uvV3 = IN[2].uv;
                    o.color = IN[i].color;
                    tristream.Append(o);
                }
            }

            float area(float2 p1, float2 p2, float2 p3)
            {
                return abs(p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)) * 0.5f;
            }

            float3 BarycentricCoordinates(float2 p, float2 v0, float2 v1, float2 v2)
            {
                float2 v0v1 = v1 - v0;
                float2 v0v2 = v2 - v0;
                float2 v0p = p - v0;

                float d00 = dot(v0v1, v0v1);
                float d01 = dot(v0v1, v0v2);
                float d11 = dot(v0v2, v0v2);
                float d20 = dot(v0p, v0v1);
                float d21 = dot(v0p, v0v2);

                float denom = d00 * d11 - d01 * d01;

                float v = (d11 * d20 - d01 * d21) / denom;
                float w = (d00 * d21 - d01 * d20) / denom;
                float u = 1.0 - v - w;

                return float3(u, v, w);
            }

            // chek if a point is in triangle
            bool pointInTriangle(float2 p, float2 v0, float2 v1, float2 v2)
            {
                float3 bary = BarycentricCoordinates(p, v0, v1, v2);
                //Point is inside only if all barycentric are in range 0,1
                return (bary.x >= -0.0 && bary.x <= 1.0) &&
                (bary.y >= -0.0 && bary.y <= 1.0) &&
                (bary.z >= -0.0 && bary.z <= 1.0);
            }

            bool uvInBound(float2 uv)
            {
                return uv.x >= 0 && uv.x <= 1 && uv.y >= 0 && uv.y <= 1;
            }

            half4 get_color(sampler2D text, float2 uv)
            {
                return tex2D(text, uv);
            }


            bool is_colored(half4 color)
            {
                return color.r > 0.99 && color.g > 0.99 && color.b > 0.99;
            }

            half4 search_for_colored_pixel(float2 uv, sampler2D text, float2 texelSize, g2f IN)
            {
                // Verifica se il primo pixel è colorato
                half4 pixel_color = get_color(text, uv);
                if(is_colored(get_color(_Positions, uv)))
                {
                    return pixel_color;
                }

                int directions[4][2] = {
                    {1, 0},
                    {0, 1},
                    {-1, 0},
                    {0, -1}
                };

                //search colored pixel
                int dim = 0;
                [loop]
                for(int h = 0; h < _RadiusSearch; h++)
                {
                    dim += 2;
                    uv = uv + float2(-1, -1) * texelSize;
                    for(int i = 0; i < 4; i++)
                    {
                        int dx = directions[i][0];
                        int dy = directions[i][1];
                        for(int j = 0; j < dim; j++)
                        {
                            uv = uv + float2(dx, dy) * texelSize;
                            //check uv is in bounds and is in triangle 
                            if(uvInBound(uv) && pointInTriangle(uv, IN.uvV1, IN.uvV2, IN.uvV3))
                            {
                                half4 color = get_color(text, uv);
                                if(is_colored(get_color(_Positions, uv)))
                                {
                                    return color;
                                }
                            }
                        }

                    }
                }
                return IN.color;
                // return half4(1,0,1,1);
            }

            half4 addShadow(half4 color, g2f i)
            {
                // Base color
                half4 baseColor = color;
                half3 normal = normalize(i.normal);

                // diffuse lighting
                half3 lightDir = normalize(_WorldSpaceLightPos0.xyz);
                half  diff = max(0, dot(normal, lightDir));
                half  inverse_diff = max(0, dot(normal, -lightDir));

                half3 lighting = baseColor.rgb * 0.02 + (baseColor.rgb * _WorldColor.rgb + diff * baseColor.rgb * 0.9 - inverse_diff * baseColor.rgb *
                    0.1) * 0.98;

                return half4(lighting, baseColor.a);
            }

            // Fragment Shader
            half4 frag(g2f i) : SV_Target
            {
                float2 texelSize = float2(_PointsTex_TexelSize.x, _PointsTex_TexelSize.y); //x,y values rapresents the texel sizes

                //convert to texture position and riconvert to uv posion
                uint2  xy = round(i.uv * float2(_PointsTex_TexelSize.z, _PointsTex_TexelSize.w));
                float2 uv = xy * texelSize;
                half4  foundedColor = search_for_colored_pixel(uv, _PointsTex, texelSize, i);
                if(_Invert_colors == 1)
                {
                    foundedColor = half4(foundedColor.b, foundedColor.g, foundedColor.r, foundedColor.a);
                }
                return _ColorMult * addShadow(foundedColor, i);

            }
            ENDCG
        }

        Pass
        {
            Name "OUTLINE"
            Tags
            {
                "LightMode" = "Always"
            }
            Blend SrcAlpha OneMinusSrcAlpha

            Cull Front // Render only faces facing away from the camera

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            // Uniforms
            half  _OutlineWidth;
            half4 _OutlineColor;

            // Function to calculate the outline position
            float4 vert(appdata_full v) : SV_POSITION
            {
                // Transform position to clip space
                float4 clipPosition = UnityObjectToClipPos(v.vertex);

                // Calculate the normal in clip space
                float3 clipNormal = mul((float3x3)UNITY_MATRIX_VP, mul((float3x3)UNITY_MATRIX_M, v.normal));

                // Offset position in 2D space
                float2 offset = normalize(clipNormal.xy) / _ScreenParams.xy * _OutlineWidth * clipPosition.w * 2;

                // Apply the offset in clip space
                clipPosition.xy += offset;

                return clipPosition;
            }

            // Fragment shader for the outline color
            half4 frag() : SV_Target
            {
                return _OutlineColor; // Return the outline color
            }
            ENDCG
        }
    }
    Fallback "Diffuse"
}