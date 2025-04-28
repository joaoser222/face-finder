<template>
  <div class="d-flex flex-row flex-sm-column align-center justify-start rounded-lg bg-black pa-2 h-sm-100 w-100">
    <!-- Logo -->
    <div class="d-flex justify-center align-center pl-2 pr-5 pr-sm-2 py-2 pb-sm-6">
      <v-img src="@/assets/logo.svg" width="64" height="64"></v-img>
    </div>
      
    
    <!-- Menu items -->
    <div class="flex-grow-1 d-flex flex-row flex-sm-column align-center justify-end justify-sm-start">
      <v-btn
        v-for="item in menuItems"
        :key="item.icon"
        :to="item.to"
        color="white"
        variant="text"
        height="48"
        class="mb-sm-4"
        v-tooltip.bottom="item.tooltip"
      >
        <v-icon :size="$vuetify.display.smAndUp ? 28 : 24">{{ item.icon }}</v-icon>
      </v-btn>
    </div>
    
  </div>
</template>

<script setup>
  const menuItems = [
    { icon: 'Photo', to: '/collections', tooltip: 'Coleções' },
    { icon: 'UserSearch', to: '/searches', tooltip: 'Pesquisas' },
    { icon: 'Settings', to: '/settings', tooltip: 'Configurações' },
    { icon: 'Logout', to: '/logout', tooltip: 'Logout' },

  ]
</script>

<style>

</style>