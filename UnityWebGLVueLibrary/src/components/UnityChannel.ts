import type { Callback, EventName, UnityInstance } from '@/types'
import UnityGlobalChannel from '@/components/UnityGlobalChannel'

/**
 * Class representing a communication channel between JavaScript and Unity.
 * Provides methods to send messages to Unity objects and receive events from the Unity instance.
 */
export default class UnityChannel {
  get isActive(): boolean {
    return this._isActive
  }

  private readonly _unityInstance: UnityInstance
  private _globalChannel: UnityGlobalChannel
  private _isActive: boolean

  /**
   * @param {UnityInstance} unityInstance - The instance of Unity to communicate with.
   * @param {string} [channelName="_UNITY_CHANNEL"] - Optional name for the global channel.
   */
  constructor(unityInstance: UnityInstance, channelName: string = '_UNITY_CHANNEL') {
    this._unityInstance = unityInstance
    if (!window[channelName]) {
      window[channelName] = new UnityGlobalChannel()
    }
    this._globalChannel = window[channelName]
    this._isActive = true
  }

  /**
   * Calls a function of a Unity object.
   *
   * @param {string} objectName - The name of the Unity object to call the function from.
   * @param {string} methodName - The method name on the Unity object to invoke.
   * @param {any} [param] - Optional parameter to pass to the Unity method.
   */
  call(objectName: string, methodName: string, param?: number | string) {
    if (!this._isActive) {
      throw new Error(
        'Cannot invoke call() on a Unity instance that has already been quit. Please ensure the instance is active before making calls.'
      )
    }
    this._unityInstance.SendMessage(objectName, methodName, param)
  }

  /**
   * Sets the Unity instance to fullscreen or exits fullscreen mode.
   *
   * @param {boolean} isFullscreen - If true, Unity will switch to fullscreen; if false, it will exit fullscreen.
   */
  setFullscreen(isFullscreen: boolean) {
    if (!this._isActive) {
      throw new Error(
        'Cannot invoke setFullscreen() on a Unity instance that has already been quit. Please ensure the instance is active before making calls.'
      )
    }
    this._unityInstance.SetFullscreen(isFullscreen ? 1 : 0)
  }

  /**
   * Subscribes a callback to an event from Unity.
   *
   * @param {EventName} eventName - The name of the event to subscribe to
   * @param {Callback} callback - The callback function to execute when the event is triggered
   * @param {boolean} [once=false] - Optional boolean indicating if the callback should only be executed once
   */
  subscribe(eventName: EventName, callback: Callback, once: boolean = false): void {
    if (!this._isActive) {
      throw new Error(
        'Cannot subscribe event on a Unity instance that has already been quit. Please ensure the instance is active before making calls.'
      )
    }
    this._globalChannel.subscribe(eventName, callback, once)
  }

  /**
   * Unsubscribes a callback from an event.
   *
   * @param {EventName} eventName - The name of the event to unsubscribe from
   * @param {Callback} callback - The callback function
   */
  unsubscribe(eventName: EventName, callback: Callback): void {
    if (!this._isActive) {
      throw new Error(
        'Cannot unsubscribe event on a Unity instance that has already been quit. Please ensure the instance is active before making calls.'
      )
    }
    this._globalChannel?.unsubscribe(eventName, callback)
  }

  /**
   * Quits the Unity instance and clears all subscriptions from the global channel.
   *
   * @returns {Promise<void>} - A promise that resolves when the Unity instance has quit.
   */
  async quit(): Promise<void> {
    if (!this._isActive) {
      throw new Error(
        'Cannot invoke quit() on a Unity instance that has already been quit. Please ensure the instance is active before making calls.'
      )
    }
    this._globalChannel?.clear()
    await this._unityInstance.Quit()
    this._isActive = false
  }

  //the publish function should be accessible from Unity jslib only (globalchannel)
  // publish(eventName: EventName, ...args: any[]): any {
  //     return this._globalChannel?.publish(eventName, ...args);
  // }
}
