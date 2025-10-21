import type { Callback, EventName } from '@/types'

/**
 * Class representing a global event channel for Unity.
 * Manages the subscription, execution, and unsubscription of events.
 * Each event can have multiple callbacks, and each callback can be marked
 * to be executed once or multiple times.
 * This class should be used only in Unity to publish or wrapped in the UnityChannel class
 */
export default class UnityGlobalChannel {
  /**
   * A map that stores event names as keys. Each event name maps to another map of callbacks.
   * The callback map contains the callback functions and a boolean indicating if they should be executed only once.
   */
  events: Map<EventName, Map<Callback, boolean>>

  constructor() {
    this.events = new Map()
  }

  /**
   * Subscribes a callback to a specific event.
   * @param {EventName} eventName - The name of the event to subscribe to.
   * @param {Callback} callback - The callback function to be executed when the event is published.
   * @param {boolean} [once=false] - Optional boolean that specifies if the callback should only be executed once (after that it will automatically be unsubscribed).
   *                                  Defaults to false, meaning the callback can be executed multiple times.
   */
  subscribe(eventName: EventName, callback: Callback, once: boolean = false): void {
    //If the event does not already exist, it creates a new entry for the event.
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Map())
    }
    this.events.get(eventName)?.set(callback, once)
  }

  /**
   * Unsubscribes a specific callback from a given event.
   *
   * @param {EventName} eventName - The name of the event from which the callback will be removed.
   * @param {Callback} callback - The callback function to unsubscribe from the event.
   */
  unsubscribe(eventName: EventName, callback: Callback): void {
    //If the event or callback does not exist, nothing happens.
    if (!this.events.has(eventName)) {
      return
    }
    this.events.get(eventName)?.delete(callback)
  }

  /**
   * Clears all events and their callbacks from the channel.
   * This removes all subscriptions.
   */
  clear(): void {
    this.events.clear()
  }

  /**
   * Publishes an event, executing all callbacks associated with the given event name.
   * Returns the value of the last executed callback.
   *
   * This method is intended to be executed in Unity in the jslib file.
   *
   * @param {EventName} eventName - The name of the event to publish.
   * @param {...any[]} args - arguments passed to the callback functions.
   * @returns {any} - Returns the value of the last callback executed.
   */
  publish(eventName: EventName, ...args: unknown[]): unknown | undefined {
    let ret
    if (this.events.has(eventName)) {
      this.events.get(eventName)?.forEach((once, callback) => {
        if (once) {
          //If a callback is marked to be executed only once, it will be removed after execution.
          this.events.get(eventName)?.delete(callback)
        }
        ret = callback(...args)
      })
    }
    return ret
  }
}
