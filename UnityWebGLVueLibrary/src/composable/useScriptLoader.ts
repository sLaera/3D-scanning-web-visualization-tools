import { ref } from 'vue';

const loadedScripts = ref<Set<string>>(new Set());

export function useScriptLoader() {
  /**
   * Dynamically loads an external script by creating and appending a <script> element to the document. If the script has already loaded, the promise resolves with null
   *
   * @param {string} src - The URL of the script to load.
   * @returns {Promise<HTMLScriptElement | null>} - A promise that resolves when the script is loaded successfully, or rejects if the loading fails.
   */
  const loadScript = (src: string): Promise<HTMLScriptElement | null> => {
    return new Promise((resolve, reject) => {
      if (loadedScripts.value.has(src)) {
        resolve(null);
        return;
      }

      //create a new tag script with the given source.
      const script = document.createElement('script')
      script.src = src
      script.async = true
      script.onload = () => {
        loadedScripts.value.add(src);
        resolve(script)
      }
      script.onerror = (err) => {
        script.remove()
        if (typeof err === 'string') {
          reject(new Error(`Failed to load script ${src}\nwith error:\n${err}`))
        }
        reject(new Error(`Failed to load script ${src}`))
      }
      document.body.appendChild(script)
    });
  };

  return { loadScript, isLoaded: (src: string) => loadedScripts.value.has(src) };
}