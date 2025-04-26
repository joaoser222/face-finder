<template>
  <div class="d-flex flex-column align-start justify-center flex-grow-1 py-3">
    <div class="mb-3 w-100">
      <h1>
        <slot name="title"></slot>
      </h1>
    </div>
    <div class="d-flex flex-column justify-start align-end my-4 w-100">
      <slot name="actions"></slot>
    </div>
    <v-card class="w-100 h-100 pa-3">
      <v-card-text>
        <slot name="default"></slot>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'PageContainer'
}
</script>