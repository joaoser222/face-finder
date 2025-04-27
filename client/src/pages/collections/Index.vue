<template>
  <image-grid-page
    :title="'Coleções'"
    :endpoint="'collections/list'"
    :empty-title="'Gerencie suas coleções de fotos'"
    :empty-description="`
      Coleções são grupos de fotos que você deve criar para utilizar o algoritmo de pesquisa.
    `"
    @select="selectItem"
    :status-options="statusOptions"
  >
    <template #actions="{getItems}">
      <component :is="CollectionForm" @success="getItems()" />
    </template>
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
      <v-btn icon="Trash" 
        @click="deleteItem(item,'Coleção',item.name,`/collections/delete/${item.id}`)"
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
import CollectionForm from './Form.vue';
import statusOptions from './statusOptions';

const router = useRouter();

const selectItem = (item) => {
  const route = `/collections/${item.id}`;
  router.push(route);
}
</script>