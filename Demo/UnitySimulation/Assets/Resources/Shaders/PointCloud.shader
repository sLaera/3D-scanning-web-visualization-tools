Shader "Custom/PointCloud"
{
    Properties
    {
        _Color("Color", Color) = (1,1,1,1)
        _Normal("Normal", Vector) = (0,0,0,0)
        _PointScale("Point Scale", Float) = 1
    }
    SubShader
    {
        Tags
        {
            "RenderType"="Opaque"
        }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing

            #include "UnityCG.cginc"


            UNITY_INSTANCING_BUFFER_START(Props)
                UNITY_DEFINE_INSTANCED_PROP(float4, _Color)
                UNITY_DEFINE_INSTANCED_PROP(float4, _Normal)
                UNITY_DEFINE_INSTANCED_PROP(float, _PointScale)
            UNITY_INSTANCING_BUFFER_END(Props)

            struct appdata {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct v2f {
                float4 vertex : SV_POSITION;
                float4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float3x3 rotation_matrix_from_vectors(float3 source, float3 target)
            {
                //Apply Rodrigues formula
                source = normalize(source);
                target = normalize(target);

                //identity matrix
                float3x3 I = float3x3(1, 0, 0, 0, 1, 0, 0, 0, 1);

                float3 tangent = cross(source, target);
                float  dotProduct = dot(source, target);

                //the two vector are parallel. Don't rotate
                if(abs(dotProduct - 1.0) < 1e-6)
                {
                    return I;
                }
                //the two vectors have opposite directions
                if(abs(dotProduct + 1.0) < 1e-6)
                {
                    float3 orthogonal = abs(source.x) < 0.99 ? float3(1, 0, 0) : float3(0, 1, 0);
                    tangent = normalize(cross(source, orthogonal));
                    float3x3 K = float3x3(0, -tangent.z, tangent.y, tangent.z, 0, -tangent.x, -tangent.y, tangent.x, 0);
                    return I + 2.0 * mul(K, K);
                }

                float3x3 v_mat = float3x3(0, -tangent.z, tangent.y, tangent.z, 0, -tangent.x, -tangent.y, tangent.x, 0);
                return I + v_mat + mul(v_mat, v_mat) * (1 / (1 + dotProduct));
            }

            v2f vert(appdata v)
            {
                v2f o;
                UNITY_SETUP_INSTANCE_ID(v);

                float3 normal = normalize(UNITY_ACCESS_INSTANCED_PROP(Props, _Normal));

                //Compute CrossProduct between Camera forward vector and normal position
                //The cross product indicate how closly the normal face the camera direction
                float3 viewDir = normalize(UNITY_MATRIX_IT_MV[2].xyz);
                float3 dotProduct = dot(normal, viewDir);
                //Convert product to a value of lightness (between 0.1 and 1)
                float remappedDot = 0.1 + 0.9 * ((dotProduct + 1) / 2);

                //Scale instance
                float dist = distance(_WorldSpaceCameraPos, mul(unity_ObjectToWorld, v.vertex));
                float scale = UNITY_ACCESS_INSTANCED_PROP(Props, _PointScale);
                scale *= sqrt(dist);
                float4x4 scaleMatrix = float4x4(
                    scale, 0, 0, 0,
                    0, scale, 0, 0,
                    0, 0, scale, 0,
                    0, 0, 0, scale
                );
                v.vertex = mul(scaleMatrix, v.vertex);

                // ---- Rotate in direction of camera ----
                // float4 cameraLocalPos = mul(unity_WorldToObject, float4(_WorldSpaceCameraPos, 1.0));
                // //rotate forward vector towards camera vector
                // float3x3 rotMatrix = rotation_matrix_from_vectors(float3(1, 0, 0), cameraLocalPos.xyz);
                // v.vertex.xyz = mul(rotMatrix, v.vertex.xyz);

                o.vertex = UnityObjectToClipPos(v.vertex);
                float4 color = UNITY_ACCESS_INSTANCED_PROP(Props, _Color);
                o.color = remappedDot * color;
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                return i.color;
            }
            ENDCG
        }
    }
}