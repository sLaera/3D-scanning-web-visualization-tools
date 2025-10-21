<script setup lang="ts">
import UnityInstance from '@/components/DemoInstanceUnityWrapper.vue'
import { ref } from 'vue'

const nInstancesInput = ref<string>("1")
const currentNInstances = ref<number>(Number(nInstancesInput.value))

let setNInstances = () => {
  currentNInstances.value = Number(nInstancesInput.value)
}

</script>

<template>
  <div class="flex items-center justify-center w-full">
    <div class="flex gap-4">
      <FloatLabel>
        <InputText id="instances_label" v-model="nInstancesInput" type="number" min="1" />
        <label for="instances_label">Number of instances</label>
      </FloatLabel>
      <Button
        type="button"
        @click="setNInstances"
      >
        Submit
      </Button>
    </div>
  </div>
  <div class="grid grid-cols-2 gap-2 mt-6">
    <div v-for="i in currentNInstances" :key="i">
      <Card>
        <template #content>
          <UnityInstance :postfix="'_' + i"/>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped></style>
