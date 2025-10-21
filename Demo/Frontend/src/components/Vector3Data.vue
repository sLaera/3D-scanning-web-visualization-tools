<script setup lang="ts">
import type { Vector3 } from '@/types/api'

defineProps<{
  vector : Vector3
}>();


</script>

<template>
  <ul class="list-none">
    <li>
      x: {{ vector.x }}
    </li>
    <li>
      y: {{ vector.y }}
    </li>
    <li>
      z: {{ vector.z }}
    </li>
  </ul>
</template>

<style scoped lang="scss">

</style>