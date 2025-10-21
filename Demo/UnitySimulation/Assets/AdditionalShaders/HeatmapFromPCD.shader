Shader "Custom/HeatmapFromPCD"
{
    Properties
    {
        _BaseColor("No point color", Color) = (0.5, 0.5, 0.5, 1)
        _NoFoundColor("No found color", Color) = (0, 0, 0, 1)
    }
    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
        }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma geometry geom
            #include "UnityCG.cginc"

            StructuredBuffer<float2> _Points : register(t0);
            StructuredBuffer<float4> _Colors : register(t1);
            int                      _PointCount = 0;
            float4                   _BaseColor;
            float4                   _NoFoundColor;

            struct v2g {
                float2 uv : TEXCOORD0;
                float4 vertex : POSITION;
            };

            v2g vert(appdata_full v)
            {
                v2g o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord;
                return o;
            }

            struct g2f {
                float2 uv : TEXCOORD0;
                float4 vertex : POSITION;
                float2 uvV1 : TEXCOORD1; // fist vertex of the triangle face
                float2 uvV2 : TEXCOORD2; // second vertex of the triangle face
                float2 uvV3 : TEXCOORD3; // third vertex of the triangle face
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
                    o.uvV1 = IN[0].uv;
                    o.uvV2 = IN[1].uv;
                    o.uvV3 = IN[2].uv;
                    tristream.Append(o);
                }
            }

            float area(float2 p1, float2 p2, float2 p3)
            {
                return abs(p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)) * 0.5;
            }

            // chek if a point is in triangle
            bool pointInTriangle(float2 p, float2 uvV1, float2 uvV2, float2 uvV3)
            {
                float A = area(uvV1, uvV2, uvV3);
                float A1 = area(p, uvV2, uvV3);
                float A2 = area(uvV1, p, uvV3);
                float A3 = area(uvV1, uvV2, p);
                // point is in triangle if sum of areas is equal to total area
                return (A - (A1 + A2 + A3)) <= 0.0000001;
            }

            float distanceSquared(float2 a, float2 b)
            {
                return (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y);
            }

            // Fragment Shader
            half4 frag(g2f i) : SV_Target
            {
                if(_PointCount <= 0)
                {
                    return half4(_BaseColor);
                }

                bool found = false;
                //founded nearest points
                float2 v1 = float2(-1, -1);
                //founded nearest points indexes
                int i1 = 0;
                for(int j = 0; j < _PointCount; j++)
                {
                    float2 p = _Points[j];
                    float  distP = distanceSquared(p, i.uv);

                    //For debug purpose draw a circle around the point
                    // half4 ret = half4(0, 0, 0, 0);
                    // bool  isPointClose = false;
                    // if(distP < 0.0001)
                    // {
                    //     ret = half4(1, 1, 1, 1);
                    //     isPointClose = true;
                    // }
                    // if(distP < 0.00005)
                    // {
                    //     ret = half4(0, 0, 0, 1);
                    // }
                    // if(distP < 0.00001)
                    // {
                    //     ret = _Colors[j];
                    // }
                    // if(isPointClose)
                    // {
                    //     return ret;
                    // }

                    if(pointInTriangle(p, i.uvV1, i.uvV2, i.uvV3))
                    {
                        found = true;
                        float distV1 = distanceSquared(v1, i.uv);
                        // set the nearest point
                        if(distP < distV1)
                        {
                            v1 = p;
                            i1 = j;
                        }
                    }
                    // else if(found)
                    // {
                    //     //a point before is found, this point is outside of triangle. All points are founded (points are sorted by triangle position)
                    //     break;
                    // }
                }

                return half4(found ? _Colors[i1] : _NoFoundColor);
                // texture sampeling
                // half4 texColor = tex2D(_MainTex, i.uv)
            }
            ENDCG
        }
    }
    Fallback "Diffuse"
}