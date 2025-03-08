<template>
  <v-layout class="mw-100 mh-100">
    <!-- Barra lateral escura -->
    <v-navigation-drawer
      permanent
      color="transparent"
      width="100"
      class="d-flex flex-column align-center pa-2 position-fixed"
      border="0"
      v-if="$vuetify.display.smAndUp"
    >
      <Toolbar />
    </v-navigation-drawer>
    <v-app-bar
      color="transparent"
      height="80"
      class="d-flex flex-column align-center pa-2 position-fixed"
      v-else
    >
      <Toolbar />
    </v-app-bar>

    <!-- Conteúdo principal -->
    <v-main class="bg-grey-lighten-4">
      <v-container fluid class="pt-8 px-6 h-100 w-100">
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import Toolbar from '@/pages/reusables/Toolbar.vue'
</script>

<style scoped>
.v-navigation-drawer :deep(.v-list-item) {
  min-height: 44px;
  padding: 8px;
  justify-content: center;
}

.v-navigation-drawer :deep(.v-list) {
  background-color: transparent;
}
</style>