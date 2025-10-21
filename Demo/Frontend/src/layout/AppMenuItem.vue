<script setup lang="ts">
import { useLayout } from '@/layout/composables/layout.js'
import { onBeforeMount, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const { layoutState, setActiveMenuItem, onMenuToggle } = useLayout()

const props = withDefaults(
  defineProps<{
    item: MenuItem
    index?: number
    root?: boolean
    parentItemKey?: string | null
  }>(),
  {
    index: 0,
    root: true,
    parentItemKey: null
  }
)

const isActiveMenu = ref<boolean>(false)
const itemKey = ref<string | null>(null)

onBeforeMount(() => {
  itemKey.value = props.parentItemKey
    ? props.parentItemKey + '-' + props.index
    : String(props.index)

  const activeItem = layoutState.activeMenuItem

  isActiveMenu.value =
    activeItem === itemKey.value || (activeItem?.startsWith(itemKey.value + '-') as boolean)
})

watch(
  () => layoutState.activeMenuItem,
  (newVal) => {
    isActiveMenu.value =
      newVal === itemKey.value || (newVal?.startsWith(itemKey.value + '-') as boolean)
  }
)

function itemClick(event: Event, item: MenuItem) {
  if (item.disabled) {
    event.preventDefault()
    return
  }

  if ((item.to || item.url) && layoutState.staticMenuMobileActive) {
    onMenuToggle()
  }

  const foundItemKey: string | null = item.items
    ? isActiveMenu.value
      ? props.parentItemKey
      : itemKey.value
    : itemKey.value

  setActiveMenuItem(foundItemKey)
}

function checkActiveRoute(item: MenuItem) {
  return route.path === item.to
}
</script>

<template>
  <li :class="{ 'layout-root-menuitem': root, 'active-menuitem': isActiveMenu }">
    <div v-if="root" class="layout-menuitem-root-text">
      {{ item.label }}
    </div>
    <a
      v-if="!item.to || item.items"
      :href="item.url"
      @click="itemClick($event, item)"
      :class="item.class"
      :target="item.target"
      tabindex="0"
    >
      <i :class="item.icon" class="layout-menuitem-icon"></i>
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <i class="pi pi-fw pi-angle-down layout-submenu-toggler" v-if="item.items"></i>
    </a>
    <router-link
      v-if="item.to && !item.items"
      @click="itemClick($event, item)"
      :class="[item.class, { 'active-route': checkActiveRoute(item) }]"
      tabindex="0"
      :to="item.to"
    >
      <i :class="item.icon" class="layout-menuitem-icon"></i>
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <i class="pi pi-fw pi-angle-down layout-submenu-toggler" v-if="item.items"></i>
    </router-link>
    <Transition v-if="item.items" name="layout-submenu">
      <ul v-show="root ? true : isActiveMenu" class="layout-submenu">
        <app-menu-item
          v-for="(child, i) in item.items"
          :key="child as any"
          :index="i"
          :item="child"
          :parentItemKey="itemKey"
          :root="false"
        ></app-menu-item>
      </ul>
    </Transition>
  </li>
</template>

<style lang="scss" scoped></style>
