import { useScriptLoader } from '@/composable/useScriptLoader.ts'
import { createUnityInstance, UnityConfigs, UnityInstance } from '@/types.ts'
import { ref } from 'vue'

// Map loader script to its corresponding createUnityInstance function
const loaderFunctions = ref<Map<string, createUnityInstance>>(new Map())

export function useUnityLoader() {
  const { loadScript, isLoaded } = useScriptLoader()
  return {
    /**
     * Loads a Unity instance into a given HTML canvas element.
     * This function first loads the Unity loader script using `loadExternalScript`,
     * and then creates the Unity instance with the provided configuration.
     *
     * @param {HTMLCanvasElement} canvas - The canvas element where Unity will render the game.
     * @param {UnityConfigs} config - The configuration object required to initialize the Unity instance. https://docs.unity3d.com/Manual/webgl-templates.html
     * @param {(progress: number) => void} onProgress - A callback function that receives progress updates during Unity's loading process.
     * @return {Promise<UnityInstance>} - Resolves when Unity has been successfully initialized with the unity instance.
     */
    loadUnity: async (
      canvas: HTMLCanvasElement,
      config: UnityConfigs,
      onProgress: (progress: number) => void
    ): Promise<UnityInstance> => {
      //if not already present, add loader script
      if (!isLoaded(config.loaderUrl) || !loaderFunctions.value.has(config.loaderUrl)) {
        await loadScript(config.loaderUrl)
        if (!window.createUnityInstance) {
          throw new Error('Unable to load unity loader')
        }

        // Each loader script has its own createUnityInstance function.
        // So each function is stored in a map and removed from `window` so it's not globally accessible.
        // By doing that, it prevents unwanted usage of loading functino to a different unity project
        loaderFunctions.value.set(
          config.loaderUrl,
          window.createUnityInstance as createUnityInstance
        )
        window.createUnityInstance = undefined
      }

      const foundedLoaderFunction = loaderFunctions.value.get(config.loaderUrl)
      if (!foundedLoaderFunction) {
        throw new Error('Unable to load unity loader')
      }
      return await foundedLoaderFunction(canvas, config, onProgress)
    }
  }
}
