<template>
  <div class="d-flex flex-column align-start justify-center w-100 h-100 py-3">
    <div class="mb-3 w-100">
      <h1>
        <slot name="title"></slot>
      </h1>
    </div>
    <div class="d-flex flex-row justify-end align-center my-4 w-100">
      <slot name="action-buttons"></slot>
    </div>
    <v-card class="w-100 pa-3 flex-grow-1">
      <v-card-text>
        <div class="d-flex justify-space-between align-center mb-4" v-if="showSearch && (!noItems || search)">
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
                @click="handleSearch"
              >
              </v-btn>
            </template>
            </v-text-field>
          </div>
        </div>

        <slot name="default"></slot>

        <v-empty-state v-if="search && noItems">
          <template v-slot:media>
            <div class="d-flex flex-column justify-center align-center">
              <v-icon icon="Search" size="100" color="primary" style="stroke-width: 1.0px"></v-icon>
            </div>
          </template>

          <template v-slot:title>
            <div class="text-h6 mt-8">
              Nenhum resultado encontrado
            </div>
          </template>

          <template v-slot:text>
            <div class="text-caption">
              Não há itens correspondentes à sua pesquisa
            </div>
          </template>
        </v-empty-state>

        <!-- Estado vazio -->
        <v-empty-state v-else-if="noItems">
          <template v-slot:media>
            <div class="d-flex flex-column justify-center align-center">
              <slot name="no-items-banner"></slot>
            </div>
          </template>

          <template v-slot:title>
            <div class="text-h6 mt-8">
              <slot name="no-items-subtitle"></slot>
            </div>
          </template>

          <template v-slot:text>
            <div class="text-caption">
              <slot name="no-items-description"></slot>
            </div>
          </template>
        </v-empty-state>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name:'BasePage',
  props:{
    showSearch: {
      type: Boolean,
      default: true
    },
    noItems: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      search: '',
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', this.search)
    }
  }
}
</script>