<template>
  <v-autocomplete
    v-model="selectedItems"
    :items="suggestions"
    :loading="isLoading"
    :search-input="searchTerm"
    @update:search="searchTerm = $event"
    :menu-props="{ maxHeight: '400' }"
    :item-title="'name'"
    :item-value="'id'"
    
    @update:model-value="emitSelectedValues"
    multiple
    label="Coleções"
    :placeholder="placeholder"
    return-object
    chips
    closable-chips
    no-filter
    hide-selected
    clear-on-select
    :rules="[validations.required]"
  >
    <template #no-data>
      <div class="text-subtitle-1 text-center pa-2">
        {{ placeholder }}
      </div>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="item.raw.name" />
    </template>
    <template #chip="{ props, item }">
      <v-chip 
        v-bind="props" 
        :title="item.raw.name" 
        @click:close="removeSelectedItem(item.id)" 
        close-icon="X"
      />
    </template>
  </v-autocomplete>
</template>

<script setup>
import { ref, inject, watch,onMounted } from 'vue';
import { useDebounceFn } from '@vueuse/core';
import api from '@/plugins/axios';
import validations from '@/plugins/validations';

const emit = defineEmits(['update:selected', 'update:item']);

const catchRequestErrors = inject('catchRequestErrors');
const selectedItems = ref([]);
const searchTerm = ref('');
const suggestions = ref([]);
const isLoading = ref(false);
const minChars = ref(3);
const placeholder = ref('Digite o nome de coleções existentes');

// Emite os valores selecionados
const emitSelectedValues = () => {
  const values = selectedItems.value.map(item => item['id']);
  emit('update:selected', values);
  emit('update:item', selectedItems.value);
};

// Remove um item da seleção
const removeSelectedItem = (id) => {
  selectedItems.value = selectedItems.value.filter(item => item['id'] !== id);
  emitSelectedValues();
};

// Busca sugestões com debounce
const fetchSuggestions = useDebounceFn(async (term,force=false) => {
  if (term!=null && term.length < minChars.value && !force) {
    return;
  }

  try {
    isLoading.value = true;
    const response = await api.get(`searches/collections?search=${encodeURIComponent(term)}`);
    suggestions.value = response.data;
  } catch (error) {
    catchRequestErrors(error);
    suggestions.value = [];
  } finally {
    isLoading.value = false;
  }
}, 500);

watch(searchTerm, fetchSuggestions);

onMounted(() => {
  fetchSuggestions('', true);
});
</script>