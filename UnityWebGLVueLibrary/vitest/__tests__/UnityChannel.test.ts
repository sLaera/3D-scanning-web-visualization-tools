import { describe, it, vi, expect, beforeEach, afterEach } from 'vitest'
import { UnityInstance } from '../../src/types'
import UnityChannel from '../../src/components/UnityChannel'

describe('UnityChannel tests', () => {
  const mockUnityInstance: UnityInstance = {
    SendMessage: vi.fn(),
    SetFullscreen: vi.fn(),
    Quit: vi.fn()
  }

  let channel: UnityChannel

  beforeEach(() => {
    channel = new UnityChannel(mockUnityInstance)
  })

  afterEach(() => {
    delete window._UNITY_CHANNEL
    delete window._differentName
  })

  it('the global channel should be created', () => {
    expect(window._UNITY_CHANNEL).toBeDefined()
  })

  it('should create a global channel with a different name', () => {
    new UnityChannel(mockUnityInstance, '_differentName')
    expect(window._differentName).toBeDefined()
  })

  it('should use the same global channel for multiple channels', () => {
    const prevGlobalChannel = window._UNITY_CHANNEL
    new UnityChannel(mockUnityInstance)
    expect(window._UNITY_CHANNEL).toBeDefined()
    //the channel should not change
    expect(window._UNITY_CHANNEL).toBe(prevGlobalChannel)
  })

  it('should execute a subscribed callback', () => {
    const callback = vi.fn((n: number|string, s: number|string): string => '' + n + s)

    channel.subscribe('testEvent', callback)

    const result = window._UNITY_CHANNEL.publish('testEvent', 1, 'test')

    expect(callback).toHaveBeenCalledOnce()
    expect(callback).toHaveBeenLastCalledWith(1, 'test')
    expect(result).toBe('' + 1 + 'test')
  })

  it('should subscribe two callback to the same event', () => {
    const callback1 = vi.fn((n: number|string, s: number|string): string => '' + n + s)
    const callback2 = vi.fn((n: number|string, s: number|string): string => '' + s + n)

    channel.subscribe('testEvent', callback1)
    channel.subscribe('testEvent', callback2)

    const result = window._UNITY_CHANNEL.publish('testEvent', 1, 'test')

    expect(callback1).toHaveBeenCalledOnce()
    expect(callback1).toHaveBeenLastCalledWith(1, 'test')

    expect(callback2).toHaveBeenCalledOnce()
    expect(callback2).toHaveBeenLastCalledWith(1, 'test')

    expect(result).toBe('test' + 1)
  })

  it('should subscribe a callback once', () => {
    const callback = vi.fn((n: number|string, s: number|string): string => '' + n + s)

    channel.subscribe('testEvent', callback, true)

    const result1 = window._UNITY_CHANNEL.publish('testEvent', 1, 'test')
    const result2 = window._UNITY_CHANNEL.publish('testEvent', 2, 'test 2')

    expect(callback).toHaveBeenCalledOnce()
    expect(callback).toHaveBeenLastCalledWith(1, 'test')
    expect(result1).toBe('' + 1 + 'test')
    expect(result2).toBeUndefined()
  })

  it('should unsubscribe a callback', () => {
    const callback = vi.fn((n: number|string, s: number|string): string => '' + n + s)

    channel.subscribe('testEvent', callback)
    channel.unsubscribe('testEvent', callback)

    const result = window._UNITY_CHANNEL.publish('testEvent', 1, 'test')

    expect(callback).toHaveBeenCalledTimes(0)
    expect(result).toBeUndefined()
  })

  it('should quit', async () => {
    await channel.quit()
    expect(mockUnityInstance.Quit).toHaveBeenCalled()
  })
})
