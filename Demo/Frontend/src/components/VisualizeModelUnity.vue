<script setup lang="ts">
import type { UnityConfigs } from 'unity-webgl-vue'
import { UnityChannel, UnityComponent } from 'unity-webgl-vue'
import { ref, watch } from 'vue'
import { UnityStatus } from '@/classes/UnityStatus'
import { type ModelSelectOption } from '@/types/3dModel'
import type { TelemetryData } from '@/types/api'
import useTelemetry from '@/composables/useTelemetry'

const emit = defineEmits<{
  unityReady:[]
}>()

let buildUrl = '/UnityBuilds/Simulation'
const unityConfigs: UnityConfigs = {
  dataUrl: buildUrl + '/Simulation.data.gz',
  frameworkUrl: buildUrl + '/Simulation.framework.js.gz',
  codeUrl: buildUrl + '/Simulation.wasm.gz',
  loaderUrl: buildUrl + '/Simulation.loader.js'
}

const channel = ref<UnityChannel | null>(null)
const loadingProgress = ref<number>(0)
const status = ref<UnityStatus | null>(null)
const error = ref<string>()

function beforeLoad() {
  status.value = UnityStatus.BeforeLoad
}

function progress(p: number) {
  loadingProgress.value = p
  status.value = UnityStatus.Progress
}

function loaded(c: UnityChannel) {
  status.value = UnityStatus.Loaded
  channel.value = c
  emit("unityReady")
}

function onUnityError(err: Error) {
  status.value = UnityStatus.Error
  error.value = err.message
}


/**
 * Load mesh in Unity
 * @param meshInfo
 */
const loadMesh = (meshInfo: ModelSelectOption) => {
  if (!channel.value) {
    throw new Error('Unity project not loaded yet')
  }
  channel.value?.call(
    'ModelLoader',
    'Load',
    JSON.stringify({
      Url: meshInfo.url,
      Position: { x: 0, y: 0, z: 0 }
    })
  )
}


defineExpose<{ loadMesh: (meshInfo: ModelSelectOption) => void}>({
  loadMesh,
})
</script>

<template>
  <div class="flex flex-col w-full gap-2">
    <Message severity="error" v-show="!!error"> Error: {{ error }}</Message>
    <UnityComponent
      v-show="channel?.isActive"
      :unityConfigs="unityConfigs"
      width="100%"
      height="40vh"
      @beforeLoad="beforeLoad"
      @progress="progress"
      @loaded="loaded"
      @error="onUnityError"
      tabindex="-1"
      class="rounded-lg"
      style="min-height: 200px"
    />
    <div
      v-show="!channel?.isActive"
      class="rounded-lg bg-surface-950 flex flex-col"
      style="width: 100%; height: 40vh"
    >
      <!--    placeholder while loading   -->
      <div class="flex flex-col" style="margin: auto">
        <ProgressSpinner style="width: 100%" strokeWidth="8" />
        <span v-show="status === UnityStatus.Progress" class="text-primary-contrast">
          Loading {{ Math.round(loadingProgress * 100) }}%
        </span>
        <h3 v-show="status === UnityStatus.Closed" class="text-primary-contrast">Closed</h3>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
