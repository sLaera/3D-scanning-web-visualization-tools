<script setup lang="ts">
import { UnityComponent, UnityChannel } from 'unity-webgl-vue'
import type { UnityConfigs } from 'unity-webgl-vue'
import { ref, watch } from 'vue'
import { UnityStatus } from '@/classes/UnityStatus'

const { postfix } = defineProps<{ postfix: string }>()

const channel = ref<UnityChannel | null>(null)
const collisionText = ref<string>('')
const loadingProgress = ref<number>(0)
const status = ref<UnityStatus | null>(null)

let buildUrl = 'UnityBuilds/DemoUnity'
const unityConfigs: UnityConfigs = {
  dataUrl: buildUrl + '/Build.data.gz',
  frameworkUrl: buildUrl + '/Build.framework.js.gz',
  codeUrl: buildUrl + '/Build.wasm.gz',
  loaderUrl: buildUrl + '/Build.loader.js'
}

function beforeLoad() {
  console.log('+++++BEFORE LOAD+++++')
  status.value = UnityStatus.BeforeLoad
}

function progress(p: number) {
  loadingProgress.value = p
  console.log('+++++PROGRESS+++++', p)
  status.value = UnityStatus.Progress
}

function loaded(c: UnityChannel) {
  status.value = UnityStatus.Loaded
  console.log('+++++LOADED+++++', c)
  channel.value = c
}

watch(channel, async (channel) => {
  if (!channel) return

  //send to Unity the postfix of the unity instance
  channel.call('JSCommunicationHandler', 'SetEventPostfix', postfix)

  channel.subscribe(
    'HelloJS' + postfix,
    () => {
      console.log('++++++++++Game start++++++++++++')
    },
    true
  )

  channel.subscribe('Collision' + postfix, () => {
    console.log('collision')
    collisionText.value = 'collision'
    setTimeout(() => (collisionText.value = ''), 300)
  })
})

function error(err: Error) {
  console.log('+++++ERROR+++++', err)
}

function createCube() {
  channel.value?.call('floor', 'Spawn', 1)
}

function quit() {
  if (!channel.value) return
  channel.value.quit()
  status.value = UnityStatus.Closed
}

</script>

<template>
  <div v-show="status == UnityStatus.Progress">
    <h3>Loading ... {{Math.round(loadingProgress * 100)}} %</h3>
  </div>
  <div v-show="status == UnityStatus.Closed">
    <h3>Unity instance is closed</h3>
  </div>
  <div v-show="status == UnityStatus.Loaded && channel?.isActive === false">
    <h3>An error occurred</h3>
  </div>
  <div style="display: flex; width: 100%">
    <div style="width: 80%">
      <UnityComponent
        :unityConfigs="unityConfigs"
        width="100%"
        height="40vh"
        @beforeLoad="beforeLoad"
        @progress="progress"
        @loaded="loaded"
        @error="error"
        tabindex="-1"
        class="rounded-md"
      />
    </div>
    <div style="width: 20%; display: flex; flex-direction: column; gap:1rem; margin-left:1rem">
      <Button @click="quit" :disabled="!channel?.isActive" >Quit</Button>
      <Button @click="createCube" :disabled="!channel?.isActive" >New Cube</Button>
      <p>{{ collisionText }}</p>
    </div>
  </div>
</template>
