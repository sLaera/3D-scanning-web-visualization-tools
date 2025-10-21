import type { PropType } from 'vue'
import { defineComponent, h, onBeforeUnmount, onMounted, ref, useId } from 'vue'
import type { UnityConfigs } from '@/types'
import UnityChannel from '@/components/UnityChannel'
import { useUnityLoader } from '@/composable/useUnityLoader.ts'

export default defineComponent({
  name: 'UnityComponent',
  props: {
    /**
     * Configuration object for initializing the Unity instance.
     * @type {UnityConfigs}
     */
    unityConfigs: { type: Object as PropType<UnityConfigs> },
    /**
     * Width of the canvas element. Can be a string or a number.
     * Defaults to '100%'.
     * @type {string | number}
     * @default '100%'
     */
    width: {
      type: [String, Number] as PropType<string | number>,
      default: '100%'
    },
    /**
     * Height of the canvas element. Can be a string or a number.
     * Defaults to '100%'.
     * @type {string | number}
     * @default '100%'
     */
    height: {
      type: [String, Number] as PropType<string | number>,
      default: '100%'
    },
    /**
     * Tab index value of the canvas element
     * @type {string | number}
     * @default '-1'
     */
    tabindex: {
      type: [String, Number] as PropType<string | number>,
      default: '-1'
    }
  },
  emits: {
    /**
     * Emitted before the Unity instance starts loading.
     */
    beforeLoad: null,
    /**
     * Emitted periodically with the loading progress.
     * @param {number} progress - A value between 0 and 1 indicating the loading progress.
     */
    progress: (progress: number) => typeof progress == 'number',
    /**
     * Emitted when the Unity instance has been successfully loaded.
     * @param {UnityChannel} channel - The UnityChannel instance associated with the Unity instance.
     */
    loaded: (channel: UnityChannel) => channel instanceof UnityChannel,
    /**
     * Emitted if there is an error during the loading process.
     * @param {Error} error
     */
    error: (error: Error) => error instanceof Error
  },
  setup(props, { emit }) {
    const canvas = ref<HTMLCanvasElement>()
    const channel = ref<UnityChannel>()
    const { loadUnity } = useUnityLoader()

    const id = useId()
    const defaultConfigs = {
      streamingAssetsUrl: 'StreamingAssets',
      companyName: 'DefaultCompany',
      productName: 'DefaultProduct',
      channelName: '_UNITY_CHANNEL'
    }

    //merge the default configs with the ones given
    const unityConfigs: UnityConfigs = Object.assign({}, defaultConfigs, props.unityConfigs)

    onMounted(() => {
      //it's done on mounted because the canvas must not be null
      emit('beforeLoad')
      loadUnity(<HTMLCanvasElement>canvas.value, unityConfigs, (p) => {
        emit('progress', p)
      })
        .then((u) => {
          //store the channel to be able to quit before the Unmount
          channel.value = new UnityChannel(u, unityConfigs.channelName)
          emit('loaded', channel.value)
        })
        .catch((error) => {
          console.error(error)
          emit('error', error)
        })
    })

    onBeforeUnmount(() => {
      //destroy the unity instance and clear the global channel (to avoid unwanted subscriptions)
      if (channel.value?.isActive) channel.value?.quit()
    })

    return {
      canvasRef: { canvas },
      channel,
      id,
      props
    }
  },
  render() {
    //if the channel is initialized and inactive, the canvas element is removed
    if (this.channel && !this.channel.isActive) {
      return
    }

    return h(
      'canvas',
      {
        ref: this.canvasRef.canvas,
        id: this.id,
        width: this.props.width,
        height: this.props.height,
        tabindex: this.props.tabindex,
        style: {
          width: this.props.width,
          height: this.props.height
        }
      },
      []
    )
  }
})
