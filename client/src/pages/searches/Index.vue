<template>
  <image-grid-page
    title="Pesquisas de Faces"
    endpoint="searches/list"
    :form-component="Form"
    :empty-title="'Gerencie suas pesquisas de faces'"
    :empty-description="`
      Pesquisas são consultas em que você utiliza um rosto como referência para 
      encontrar imagens que contenham essa mesma face em diferentes coleções.
    `"
    :empty-banner-url="'assets/face_search.svg'"
    @select="selectItem"
  >
    <template #item-top="{ item }">
      <v-btn 
        :icon="statusOptions[item.status].icon" 
        variant="text" 
        rounded="circle" 
        density="comfortable" 
        v-tooltip="statusOptions[item.status].title" 
      >
      </v-btn>
    </template>
    <template #item-bottom="{item,deleteItem}">
      <div class="font-weight-bold text-truncate">{{ item.name }}</div>
      <v-spacer></v-spacer>
      <v-btn 
        icon="Trash" 
        @click="deleteItem(item,'Pesquisa de Face',item.name,`/searches/delete/${item.id}`)" 
        variant="text" 
        rounded="circle" 
        density="comfortable" 
        v-if="statusOptions[item.status].showDelete"
      >
      </v-btn>
    </template>
  </image-grid-page>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ImageGridPage from '../reusables/ImageGridPage.vue';
import Form from './Form.vue';
import statusOptions from './statusOptions';

const router = useRouter();

const selectItem = (item) => {
  const route = `/searches/${item.id}`;
  router.push(route);
}
</script>