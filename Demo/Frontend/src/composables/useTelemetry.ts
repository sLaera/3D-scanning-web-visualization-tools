// useTelemetry.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import type { TelemetryData } from '@/types/api'
import { host } from '@/classes/Api'
import { Utils } from '@/classes/Utils'

export default function useTelemetry(onNewTelemetry: (data: TelemetryData) => void = () => {}) {
  const telemetryHistory = ref<TelemetryData[]>([])
  const isConnected = ref(false)
  const isStreamEnded = ref(false)
  const error = ref<string | null>(null)

  let socket: Socket | null = null

  const connect = () => {
    if (socket) return

    error.value = null
    isStreamEnded.value = false

    socket = io(host)

    socket.on('connect', () => {
      console.log('Connected to telemetry server')
      isConnected.value = true
      error.value = null
    })

    socket.on('disconnect', () => {
      console.log('Disconnected from telemetry server')
      isConnected.value = false
    })

    // saves data in buffer and update state with throttle
    let historyBuffer: TelemetryData[] = []
    const handleNewData = Utils.throttle(() => {
      telemetryHistory.value.push(...historyBuffer)
      historyBuffer = []
    }, 300)
    socket.on('telemetryData', (data: TelemetryData) => {
      handleNewData()
      onNewTelemetry(data)
      historyBuffer.push(data)
    })

    socket.on('end', () => {
      console.log('Telemetry stream ended')
      isStreamEnded.value = true
    })
  }

  const startStream = () => {
    socket?.emit('start-stream')
  }

  const disconnect = () => {
    if (!socket) return

    socket.disconnect()
    socket = null
    isConnected.value = false
  }

  const sendOffFileSnippet = (snippet: string) => {
    socket?.emit('off-file-snippet', snippet)
  }

  const createOffFile = (numberOfPoints: number) : void => {
    socket?.emit('off-file-completed', numberOfPoints)
  }

  // Connect automatically when the component is mounted
  onMounted(() => {
    connect()
  })

  // Disconnect when the component is unmounted
  onUnmounted(() => {
    disconnect()
  })

  return {
    telemetryHistory,
    isConnected,
    isStreamEnded,
    error,
    connect,
    disconnect,
    startStream,
    createOffFile,
    sendOffFileSnippet
  }
}
