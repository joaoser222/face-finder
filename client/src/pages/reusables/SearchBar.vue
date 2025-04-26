<template>
  <div class="d-flex justify-space-between align-center mb-4">
    <div class="pr-2 w-100">
      <v-text-field 
        v-model="search" 
        label="Pesquisar"
        color="primary" 
        hide-details 
        single-line 
        density="compact"
        @blur="handleSearch"
      >
      <template #append-inner>
        <v-btn 
          icon="Search" 
          density="comfortable"
          color="primary"
          variant="text"
          rounded="circle" 
          @click="$emit('search', search)"
        >
        </v-btn>
      </template>
      </v-text-field>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  data: () => ({
    search: ''
  }),
  methods: {
    handleSearch() {
      this.$emit('search', this.search)
    }
  }
}
</script>
