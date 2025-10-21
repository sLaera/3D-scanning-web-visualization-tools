<script setup lang="ts">
import { onMounted, ref, useId, watch } from 'vue'
import type { ModelSelectOption } from '@/types/3dModel'
import { useRoute } from 'vue-router'
import Api from '@/classes/Api'
import LoadAndScanModelUnity from '@/components/LoadAndScanModelUnity.vue'
import { Utils } from '@/classes/Utils'
import TelemetryHistoryTable from '@/components/TelemetryHistoryTable.vue'
import { SimulationStatus } from '@/classes/SimulationStatus'
import type ModelDiffUnity from '@/components/ModelDiffUnity.vue'
import VisualizeModelUnity from '@/components/VisualizeModelUnity.vue'

const id = useId()
const route = useRoute()

const selectedModel = ref<ModelSelectOption>()
const models = ref<ModelSelectOption[]>()
const modelSelectError = ref<string | null>(null)
const reconstructError = ref<string | null>(null)
const loading = ref<boolean>(true)
const simulationUnityRef = ref<InstanceType<typeof LoadAndScanModelUnity> | null>(null)
const referenceUnityRef = ref<InstanceType<typeof LoadAndScanModelUnity> | null>(null)
const diffUnityRef = ref<InstanceType<typeof ModelDiffUnity> | null>(null)
const formError = ref<string | null>(null)
const loadedModelUrl = ref<string | null>(null)
const simulationStatus = ref<SimulationStatus>(SimulationStatus.BeforeStart)
const reconstructLoading = ref<boolean>(false)
const recompute = ref<boolean>(false)

const fetchModels = async () => {
  loading.value = true
  const { data, error: err } = await Api.getMeshes()
  if (!err && data) {
    models.value = data
  }
  modelSelectError.value = err
  loading.value = false
}
watch(() => route.params.id, fetchModels, { immediate: true })

const loadReferenceModel = () => {
  if (models.value) {
    //todo: get reference model url from server
    referenceUnityRef.value?.loadMesh(models.value[0])
  }
}

const loadModelToUnity = () => {
  formError.value = null
  if (!selectedModel.value) {
    formError.value = 'Model is required'
    return
  }
  try {
    simulationUnityRef.value?.loadMesh(selectedModel.value)
  } catch (e) {
    formError.value = Utils.getErrorMessage(e)
  } finally {
    loadedModelUrl.value = null
  }
}

const startSimulation = () => {
  simulationUnityRef.value?.startSimulation()
  simulationStatus.value = SimulationStatus.InProgress
}

const onSimulationEnd = () => {
  simulationStatus.value = SimulationStatus.Ended
}

const reconstruct = async () => {
  reconstructError.value = null
  reconstructLoading.value = true
  const { error: remeshError } = await Api.remesh({
    recompute: recompute.value,
    modelName: selectedModel.value?.name || ''
  })
  if (remeshError) {
    reconstructError.value = 'Remesh error: ' + remeshError
    reconstructLoading.value = false
    return
  }

  const { data, error } = await Api.generateDifference({
    positiveBreakpoints: [0.01, 0.04, 0.08],
    negativeBreakpoints: [0.01, -0.04, -0.08],
    modelName: selectedModel.value?.name || '',
    recompute: recompute.value
  })

  if (!data) {
    reconstructError.value = 'Diff error: ' + error
    reconstructLoading.value = false
    return
  }
  diffUnityRef.value?.visualizeDifference(data)
  reconstructLoading.value = false
}
</script>

<template>
  <div class="flex flex-col items-center justify-center w-full gap-8">
    <Card class="flex-grow" style="min-width: 400px; margin: auto; width: 50%">
      <template #content>
        <h3 class="mb-4 text-xl leading-none tracking-tight text-center">This is the reference model used for the comparison</h3>
        <VisualizeModelUnity ref="referenceUnityRef" @unityReady="loadReferenceModel" />
      </template>
    </Card>
    <div class="flex flex-col gap-4">
      <h3 class="mb-2 text-xl leading-none tracking-tight text-center">Select a model to be scanned in the simulation</h3>
      <Message severity="error" v-show="!!modelSelectError">
        Error while fetch data: {{ modelSelectError }}
        <Button @click="fetchModels" severity="secondary">Retry</Button>
      </Message>
      <div class="flex flex-col gap-1">
        <div class="flex gap-4">
          <FloatLabel class="w-full md:w-56">
            <Select
              v-model="selectedModel"
              :inputId="id"
              :options="models"
              optionLabel="name"
              class="w-full"
              :disabled="
                loading || !!modelSelectError || simulationStatus != SimulationStatus.BeforeStart
              "
              :invalid="!!formError"
            />
            <label :for="id"> Select a Model</label>
          </FloatLabel>
          <Button
            type="button"
            @click="loadModelToUnity"
            :disabled="
              loading ||
              !!modelSelectError ||
              selectedModel?.url === '' ||
              simulationStatus != SimulationStatus.BeforeStart
            "
          >
            Submit
            <ProgressSpinner
              v-show="loading"
              style="width: 1rem; height: 1rem"
              strokeWidth="8"
              fill="transparent"
              animationDuration=".5s"
            />
          </Button>
        </div>
        <Message v-if="formError" severity="error" class="message-small">{{ formError }}</Message>
      </div>
    </div>
    <div class="flex gap-4 w-full flex-wrap">
      <Card class="flex-grow" style="min-width: 400px; margin: auto; width: 50%">
        <template #content>
          <h3 class="mb-4 text-xl leading-none tracking-tight text-center">LiDAR simulation</h3>
          <LoadAndScanModelUnity
            ref="simulationUnityRef"
            @modelLoaded="(url) => (loadedModelUrl = url)"
            @simulationEnded="onSimulationEnd"
          />
        </template>
      </Card>
      <Card class="flex-grow" style="margin: auto; width: 40%">
        <template #content>
          <TelemetryHistoryTable style="height: 40vh" />
        </template>
      </Card>
    </div>
    <div class="flex flex-col gap-1">
      <Button
        v-if="simulationStatus != SimulationStatus.Ended"
        size="large"
        :disabled="loadedModelUrl === null || simulationStatus != SimulationStatus.BeforeStart"
        @click="startSimulation"
      >
        <i v-show="!reconstructLoading" class="pi pi-play-circle"></i>
        <ProgressSpinner
          v-show="reconstructLoading"
          style="width: 1rem; height: 1rem"
          strokeWidth="8"
          fill="transparent"
          animationDuration=".5s"
        />
        Start Simulation
      </Button>
      <Button v-if="simulationStatus === SimulationStatus.Ended" size="large" @click="reconstruct">
        <i v-show="!reconstructLoading" class="pi pi-arrow-circle-right"></i>
        <ProgressSpinner
          v-show="reconstructLoading"
          style="width: 1rem; height: 1rem"
          strokeWidth="8"
          fill="transparent"
          animationDuration=".5s"
        />
        Reconstruct
      </Button>
      <div class="flex items-center gap-2" v-if="simulationStatus === SimulationStatus.Ended">
        <Checkbox v-model="recompute" inputId="ingredient1" binary />
        <label> Do recompute </label>
      </div>
      <Message severity="error" v-show="!!reconstructError">
        {{ reconstructError }}
      </Message>
    </div>
    <div class="w-full">
      <Card class="w-full" style="min-width: 400px; max-width: 1000px; margin: auto">
        <template #content>
          <h3 class="mb-4 text-xl leading-none tracking-tight text-center">Visualization of the difference between the reference model and the scanned selected model</h3>
          <ModelDiffUnity ref="diffUnityRef" />
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.message-small {
  font-size: 0.8rem !important;
  background-color: transparent !important;
  outline-color: transparent !important;
  box-shadow: none !important;
}

.message-small ::v-deep(.p-message-content) {
  border: none !important;
  padding: 0 !important;
}
</style>
