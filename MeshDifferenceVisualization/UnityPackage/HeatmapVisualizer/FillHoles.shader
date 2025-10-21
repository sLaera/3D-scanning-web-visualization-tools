Shader "Custom/FillHoles"
{
    Properties
    {
        _MainTex ("Base (RGB)", 2D) = "gray" {}
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
            Name "DEPTH_PASS"
            // Scrive solo la depth, senza output di colore.
            ZWrite On
            ColorMask 0

            CGPROGRAM
            #pragma vertex vertDepth
            #pragma fragment fragDepth
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
            };

            v2f vertDepth(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                return o;
            }

            // Fragment non serve restituire un colore, il risultato va solo a scrivere la depth.
            float4 fragDepth(v2f i) : SV_Target
            {
                return 0;
            }
            ENDCG
        }

        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            Cull Back
            //            ZWrite Off
            Fog
            {
                Mode Off
            }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            fixed4 _WorldColor;
            fixed4 _ColorMult;
            int    _Invert_colors;

            struct v2f {
                float2 uv : TEXCOORD0;
                float4 vertex : POSITION;
                half4  color : COLOR0;
                float3 normal : NORMAL;
            };

            v2f vert(appdata_full v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord;
                o.color = v.color;
                o.normal = v.normal;
                return o;
            }

            half4 get_color(sampler2D text, float2 uv)
            {
                return tex2Dlod(text, float4(uv, 0, 0));
            }

            half4 addShadow(half4 color, v2f i)
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
            half4 frag(v2f i) : SV_Target
            {
                float4 baseColor = tex2D(_MainTex, i.uv);
                //dark colors are considered as holes
                if(baseColor.a < 0.99)
                {
                    baseColor = i.color;
                }
                
                if(_Invert_colors == 1)
                {
                    baseColor = half4(baseColor.b, baseColor.g, baseColor.r, baseColor.a);
                }
                return _ColorMult * addShadow(baseColor, i);

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