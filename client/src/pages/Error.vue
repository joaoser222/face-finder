<template>
  <v-main class="w-screen h-screen">
    <div class="d-flex flex-column align-center justify-center pa-4 bg-white w-100 h-100 text-center text-grey-darken-3">
      <div class="pb-5">
        <v-icon icon="RouteX" size="128" color="error"></v-icon>
      </div>
      <div class="text-h2 font-weight-bold pb-5">404</div>
      <h5 class="text-h6 font-weight-light pb-5">Oops! A página que você está procurando não foi encontrada</h5>
      <v-btn color="black" variant="flat" prepend-icon="ph ph-arrow-left" @click="$router.push('/')">Ir para página inicial</v-btn>
    </div>
  </v-main>
</template>

<script>
export default {
  name: 'ErrorPage',
}
</script>