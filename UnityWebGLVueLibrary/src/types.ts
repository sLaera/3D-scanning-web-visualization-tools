import UnityGlobalChannel from './components/UnityGlobalChannel'

/**
 * Configuration options for loading and initializing a Unity WebGL instance.
 */
export interface UnityConfigs {
  /** URL to the Unity WebGL loader script (generated after the Unity build process)*/
  loaderUrl: string
  /** URL to the Unity WebGL data file (generated after the Unity build process)*/
  dataUrl: string
  /** URL to the Unity WebGL framework file. (generated after the Unity build process) */
  frameworkUrl: string
  /** URL to the Unity WebGL code file. (generated after the Unity build process)*/
  codeUrl: string
  /** URL to the Unity WebGL memory file (optional). */
  memoryUrl?: string
  /** URL to the Unity WebGL symbols file for debugging (optional). */
  symbolsUrl?: string
  /** URL for accessing streaming assets (optional). */
  streamingAssetsUrl?: string
  /** Name of the company that owns the Unity project (optional). */
  companyName?: string
  /** Name of the Unity product (optional). */
  productName?: string
  /** Version of the Unity product (optional). */
  productVersion?: string
  /**
   * Function called when a messages such as 'error', 'warning', or 'success' is generated from the Unity instance (optional).
   * @param msg - The message to display.
   * @param type - The type of message ('error' | 'warning' | 'success').
   */
  showBanner?: (msg: string, type: 'error' | 'warning' | 'success') => void
  /** Sets the device pixel ratio for the canvas (optional).
   *
   * This field enables forcing the DPI scaling ratio for the rendered page. Set to 1 to force rendering to “standard DPI” (or non-Retina DPI), which can help performance on lower-end mobile devices. By default, this field is unset, meaning the rendered page uses the browser DPR scaling ratio, resulting in High DPI rendering.
   * */
  devicePixelRatio?: number
  /** Whether WebGL should match the canvas size (optional).
   *
   * By default, (if set to true or unset), Unity synchronizes the WebGL canvas render target size with the Document Object Model (DOM) size of the canvas element (scaled by window.devicePixelRatio). Set this to false if you want to set the canvas DOM size and WebGL render target sizes manually.
   * */
  matchWebGLToCanvasSize?: boolean
  /**
   * If set to true, all file writes inside the Unity Application.persistentDataPath directory automatically persist so that the contents are remembered when the user revisits the site the next time. If unset (or set to false), you must manually sync file modifications inside the Application.persistentDataPath directory by calling the JS_FileSystem_Sync() JavaScript function.
   */
  autoSyncPersistentDataPath?: true
  /** WebGL context attributes for fine-tuning the WebGL context (optional). */
  webglContextAttributes?: object

  /** Name of the global communication channel with Unity (optional).
   * default: _UNITY_CHANNEL
   * When handling multiple Unity instances at the same time use unique names
   *
   * */
  channelName?: string

  /** Additional properties can be included. */
  [key: string]: unknown
}

/**
 * Instance of a Unity application embedded in the web environment.
 */
export interface UnityInstance {
  /**
   * Sets the Unity application to fullscreen mode.
   * @param SetFullscreen - A value of `1` sets the application to fullscreen, `0` exits fullscreen.
   */
  SetFullscreen: (SetFullscreen: 1 | 0) => void

  /**
   * Sends a message to a Unity object, invoking a specific method.
   * @param objectName - The name of the object in Unity to send the message to.
   * @param methodName - The method to call on the specified Unity object.
   * @param value - An optional value (string or number) to pass to the method.
   */
  SendMessage: (objectName: string, methodName: string, value?: string | number) => void

  /**
   * Quits the Unity application.
   * @returns A Promise that resolves once the application has fully quit.
   */
  Quit: () => Promise<void>

  /**
   * Additional properties can be included.
   * Allows for accessing unknown properties on the UnityInstance object.
   */
  [key: string]: unknown
}

/**
 * Name of the Event in the event map of the channel
 */
export type EventName = string | symbol
/**
 * Callback of the subscribed event
 */
export type Callback = (...args: unknown[]) => unknown

/**\
 * Function exposed globally by the unity loader file
 * Creates an instance of the Unity application associated with a given HTML canvas element.
 * @param canvas - The HTML canvas element where the Unity application will be rendered.
 * @param config - The configuration settings for the Unity instance.
 * @param onProgress - A callback function that will be called with the current loading progress (0 to 1).
 * @returns Resolves to a UnityInstance when initialization is complete.
 */
export type createUnityInstance = (
  canvas: HTMLCanvasElement,
  config: UnityConfigs,
  onProgress: (progress: number) => void
) => Promise<UnityInstance>

declare global {


  interface Window {
    createUnityInstance?: createUnityInstance

    [key: string]: UnityGlobalChannel
  }
}
