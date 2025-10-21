<script setup lang="ts">
import { ref } from 'vue'
import { UnityStatus } from '@/classes/UnityStatus'
import { UnityChannel, UnityComponent } from 'unity-webgl-vue'
import type { ModelSelectOption } from '@/types/3dModel'
import type { ModelDiffInfo } from '@/types/api'

let buildUrl = '/UnityBuilds/ModelDiff'

class UnityConfigs {}

const unityConfigs: UnityConfigs = {
  dataUrl: buildUrl + '/ModelDiff.data.gz',
  frameworkUrl: buildUrl + '/ModelDiff.framework.js.gz',
  codeUrl: buildUrl + '/ModelDiff.wasm.gz',
  loaderUrl: buildUrl + '/ModelDiff.loader.js'
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
}

function onUnityError(err: Error) {
  status.value = UnityStatus.Error
  error.value = err.message
}

function toggleTarget() {
  channel.value?.call('ModelDiffVisualizer', 'ToggleTarget')
}

function toggleSource() {
  channel.value?.call('ModelDiffVisualizer', 'ToggleSource')
}

const visualizeDifference = (modelDiffInfo: ModelDiffInfo) => {
  channel.value?.call('ModelDiffVisualizer', 'LoadModelsAndTextures', JSON.stringify(modelDiffInfo))
}

defineExpose<{ visualizeDifference: (modelDiffInfo: ModelDiffInfo) => void }>({
  visualizeDifference
})
</script>

<template>
  <div class="flex flex-col w-full gap-2">
    <Message severity="error" v-show="!!error"> Error: {{ error }}</Message>
    <UnityComponent
      v-show="channel?.isActive"
      :unityConfigs="unityConfigs"
      width="100%"
      height="50vh"
      @beforeLoad="beforeLoad"
      @progress="progress"
      @loaded="loaded"
      @error="onUnityError"
      tabindex="-1"
      class="rounded-lg"
      style="min-height: 300px"
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
    <div class="flex m-auto gap-4">
      <Button label="Toggle Ground truth" @click="toggleSource" />
      <Button label="Toggle Reconstructed" @click="toggleTarget" />
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
