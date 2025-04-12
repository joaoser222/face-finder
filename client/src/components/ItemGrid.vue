<template>
  <v-row dense>
    <v-col cols="12" sm="6" md="4" lg="3" xl="2" v-for="item in items" :key="item.id">
      <v-card>
        <slot name="default" :item="item"></slot>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'ItemGrid',
  props: {
    items: {
      type: Array,
      required: true
    }
  }
}
</script>