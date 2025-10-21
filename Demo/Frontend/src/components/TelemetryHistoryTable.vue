<script setup lang="ts">
import useTelemetry from '@/composables/useTelemetry'
import Vector3Data from '@/components/Vector3Data.vue'

const { telemetryHistory } = useTelemetry()
</script>

<template>
  <DataTable :value="telemetryHistory" tableStyle="min-width: 50rem" sortField="Timestamp" :sortOrder="-1" paginator :rows="10" class="telemetry-table">
    <template #header>
      <div class="text-xl font-bold text-center">Telemetry Data</div>
    </template>
    <Column field="Timestamp" header="Timestamp" :sortable="true"></Column>
    <Column field="Position" header="Position">
      <template #body="slotProps">
        <Vector3Data :vector="slotProps.data.Position" />
      </template>
    </Column>
    <Column field="Rotation" header="Rotation">
      <template #body="slotProps">
        <Vector3Data :vector="slotProps.data.Rotation" />
      </template>
    </Column>
    <Column field="ScanFrame" header="Scanning">
      <template #body="slotProps">
        <Tag
          :severity="slotProps.data.ScanFrame ? 'success' : 'secondary'"
          :value="slotProps.data.ScanFrame ? 'scanning' : 'idle'"
          rounded
        ></Tag>
      </template>
    </Column>
  </DataTable>
</template>

<style scoped lang="scss">
.telemetry-table{
  display: flex;
  flex-direction: column;
}
.telemetry-table ::v-deep(.p-datatable-table-container){
  height: 100%;
}
</style>
