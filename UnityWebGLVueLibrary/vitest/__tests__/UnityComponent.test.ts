// UnityComponent.test.ts
import { beforeEach, describe, expect, it, MockInstance, vi } from 'vitest'
import UnityComponent from '../../src/components/UnityComponent'
import { UnityConfigs, UnityInstance } from '../../src/types'
import { mount } from '@vue/test-utils'
import { UnityChannel } from '../../src'
import { useUnityLoader } from '../../src/composable/useUnityLoader'

vi.mock('../../src/composable/useUnityLoader', () => ({
  useUnityLoader: vi.fn(() => ({ loadUnity: vi.fn(() => Promise.resolve({})) }))
}))

describe('UnityComponent', () => {
  let unityConfigs: UnityConfigs

  const mockUnityInstance: UnityInstance = {
    SendMessage: vi.fn(),
    SetFullscreen: vi.fn(),
    Quit: vi.fn()
  }

  beforeEach(() => {
    unityConfigs = {
      dataUrl: '/TEST.data',
      frameworkUrl: '/TEST.framework.js',
      codeUrl: '/TEST.wasm',
      loaderUrl: '/TEST.loader.js'
    }
  })

  it('renders the canvas with correct width and height', () => {
    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs,
        width: '500px',
        height: '400px'
      }
    })

    const canvas = wrapper.find('canvas')
    expect(canvas.element.style.width).toBe('500px')
    expect(canvas.element.style.height).toBe('400px')
  })

  it('emits beforeLoad', () => {
    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs
      }
    })

    expect(wrapper.emitted().beforeLoad.length).toBe(1)
  })

  it('calls loadUnity and emits progress and loaded events', async () => {
    ;(useUnityLoader as unknown as MockInstance).mockImplementation(() => {
      return {
        //The mock function will call on progress 3 times and resolve with progress = 1
        loadUnity: (
          canvas: HTMLCanvasElement,
          config: UnityConfigs,
          onProgress: (progress: number) => void
        ) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              onProgress(0)
            }, 100)

            setTimeout(() => {
              onProgress(0.5)
            }, 200)

            setTimeout(() => {
              onProgress(1)
              resolve(mockUnityInstance)
            }, 300)
          })
        }
      }
    })

    vi.useFakeTimers()

    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs
      }
    })
    for (let i = 0; i < 3; i++) {
      vi.advanceTimersByTime(100)
      expect(wrapper.emitted().progress[i]).toEqual([0.5 * i])
    }

    await new Promise(process.nextTick)

    //after the progress, loaded event will be emitted
    expect(wrapper.emitted()).toHaveProperty('loaded')
    expect(wrapper.emitted().loaded[0][0]._unityInstance).toEqual(mockUnityInstance)
  })

  it('emits error event if loadUnity fails', async () => {
    const mockError = new Error('TEST ERROR - Load failed')

    //Load Unity will reject the promise
    ;(useUnityLoader as unknown as MockInstance).mockImplementation(() => ({
      loadUnity: vi.fn(() => Promise.reject(mockError))
    }))

    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs
      }
    })

    await new Promise(process.nextTick)

    expect(wrapper.emitted().error.length).toBe(1)
    expect(wrapper.emitted().error[0]).toEqual([mockError])
  })

  it('quits Unity instance on unmount', async () => {
    const mockQuit = vi.fn()
    const mockUnityInstance = {
      Quit: mockQuit
    }
    ;(useUnityLoader as unknown as MockInstance).mockImplementation(() => ({
      loadUnity: vi.fn(() => Promise.resolve(mockUnityInstance))
    }))

    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs
      }
    })

    await new Promise(process.nextTick)
    wrapper.unmount()

    expect(mockQuit).toHaveBeenCalled()
  })

  it('quits Unity instance with channel.quit()', async () => {
    const mockQuit = vi.fn()
    const mockUnityInstance = {
      Quit: mockQuit
    }
    ;(useUnityLoader as unknown as MockInstance).mockImplementation(() => ({
      loadUnity: vi.fn(() => Promise.resolve(mockUnityInstance))
    }))

    const wrapper = mount(UnityComponent, {
      props: {
        unityConfigs
      }
    })

    await new Promise(process.nextTick)
    const channel = wrapper.emitted().loaded[0][0] as UnityChannel
    await channel.quit()
    expect(mockQuit).toHaveBeenCalled()
    expect(channel.isActive).toBeFalsy()
  })
})
