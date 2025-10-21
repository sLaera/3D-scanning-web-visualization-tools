Shader "Custom/HeatmapCompute"
{
    Properties
    {
        _PointsTex ("Points Texture", 2D) = "white" {}
        _Positions ("Positions Texture", 2D) = "white" {}
        _RadiusSearch ("Radius Search", Int) = 20
        _UV_length ("UV Count", Int) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
        }
        Pass
        {
            ZTest Always Cull Off ZWrite Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _PointsTex;
            sampler2D _Positions;
            float2    _Resolution;

            int _RadiusSearch;

            sampler2D _UVTex;
            int       _UV_length;
            float2    _UVTexSize;

            struct appdata {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            bool is_colored(float4 color)
            {
                return color.r > 0.99 && color.g > 0.99 && color.b > 0.99;
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
                return uv.x > 0 && uv.x < 1 && uv.y > 0 && uv.y < 1;
            }

            half4 get_color(sampler2D text, float2 uv)
            {
                return tex2Dlod(text, float4(uv, 0, 0));
            }


            float2 getUV(uint index)
            {
                uint    x = index % (int)_UVTexSize.x;
                uint    y = index / (int)_UVTexSize.x;
                float2 uv = (float2(x, y) + 0.5) / _UVTexSize;
                return tex2D(_UVTex, uv).rg;
            }

            fixed4 frag(v2f IN) : SV_Target
            {
                float2 uv = IN.uv;

                //----Search current face vertices in uv space------
                float2 uv0 = float2(-1, -1);
                float2 uv1 = float2(-1, -1);
                float2 uv2 = float2(-1, -1);
                bool   triangleFound = false;
                [loop]
                for(int j = 0; j < _UV_length; j += 3)
                {
                    if(pointInTriangle(uv, getUV(j), getUV(j + 1), getUV(j + 2)))
                    {
                        uv0 = getUV(j);
                        uv1 = getUV(j + 1);
                        uv2 = getUV(j + 2);
                        triangleFound = true;
                        break;
                    }
                }

                if(!triangleFound) return float4(0, 0, 0, 0);
                //---------------------------------------------------------

                //Current pixel is colored
                if(is_colored(get_color(_Positions, uv)))
                {
                    return get_color(_PointsTex, uv);
                }

                //-----Search neighbours colored pixels-----
                int2 directions[4] = {
                    int2(1, 0),
                    int2(0, 1),
                    int2(-1, 0),
                    int2(0, -1)
                };

                int dim = 0;
                //get xy position
                int2 searchPosXY = uv * _Resolution;
                [loop]
                for(int h = 0; h < _RadiusSearch; h++)
                {
                    dim += 2;
                    //go back by 1 pixel
                    searchPosXY -= int2(1, 1);

                    for(int i = 0; i < 4; i++)
                    {
                        //move along one of the 4 directinons by a `dim` amount
                        int2 dir = directions[i];
                        for(int j = 0; j < dim; j++)
                        {
                            searchPosXY += dir;
                            float2 searchUV = float2(searchPosXY) / _Resolution;

                            if(uvInBound(searchUV) &&
                                is_colored(get_color(_Positions, searchUV)) &&
                                pointInTriangle(searchUV, uv0, uv1, uv2))
                            {
                                return get_color(_PointsTex, searchUV);
                            }
                        }
                    }
                }

                return float4(0, 0, 0, 0); // fallback
            }
            ENDCG
        }
    }
    Fallback "Diffuse"
}