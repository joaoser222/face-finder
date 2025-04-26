<template>
  <v-empty-state>
    <template v-slot:media>
      <div class="d-flex flex-column justify-center align-center">
        <slot name="banner">
          <v-icon :icon="icon" size="128" color="grey"></v-icon>
        </slot>
      </div>
    </template>

    <template v-slot:title>
      <div class="text-h6 mt-8">
        {{ title }}
      </div>
    </template>

    <template v-slot:text>
      <div class="text-caption">
       {{ description }}
      </div>
    </template>
  </v-empty-state>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      default: 'CircleDashed'
    },
  },
  inject: ['getAssetUrl'],
  name: 'EmptyContainer'
}
</script>