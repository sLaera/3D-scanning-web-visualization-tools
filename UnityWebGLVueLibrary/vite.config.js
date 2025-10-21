import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import { resolve } from 'path';
import dts from 'vite-plugin-dts';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [dts()],
    build: {
        lib: {
            entry: resolve(__dirname, 'src/index.ts'),
            name: 'unity-webgl-vue',
            fileName: 'unity-webgl-vue'
        },
        rollupOptions: {
            external: ['vue'],
            output: {
                format: 'esm',
                inlineDynamicImports: false,
                manualChunks: function (id) {
                    if (id.includes('node_modules')) {
                        return id.toString().split('node_modules/')[1].split('/')[0].toString();
                    }
                }
            }
        },
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,
                drop_debugger: true,
                pure_funcs: ['console.log', 'console.info', 'console.debug'],
                passes: 2,
                pure_getters: true,
                unsafe_math: true,
                unsafe_methods: true
            },
            mangle: {
                safari10: true,
                properties: {
                    regex: /^_/
                }
            },
            format: {
                comments: false
            }
        }
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    }
});
