<template>
  <div>
    <base-page :no-items="noItems" @search="handleSearch">
      <template #title>
        Coleções
      </template>
      <template #no-items-banner>
        <v-img src="@/assets/collections.svg" width="350px" height="auto"></v-img>
      </template>
      <template #no-items-subtitle>
        Gerencie suas coleções de fotos
      </template>
      <template #no-items-description>
        Coleções são grupos de fotos que você deve criar para utilizar o algoritmo de pesquisa
      </template>
      <template #action-buttons>
        <collection-form @success="getItems()"></collection-form>
      </template>
      <template #default>
        <item-grid :items="items.data" v-if="items.data.length">
          <template #default="{ item }">
            <div class="position-absolute top-0 left-0 w-100 pa-2" :style="{ backgroundColor: 'transparent',zIndex: 99}" v-if="!item.status">
              <div class="d-flex align-center text-white">
                <v-spacer></v-spacer>
                <v-avatar size="32px" v-tooltip="'Upload em andamento'" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }">
                  <v-icon icon="Clock" rounded="circle" size="24px" color="white"></v-icon>
                </v-avatar>
              </div>
            </div>
            <v-img
              :src="`/api/photos/thumbnail/${item.thumbnail_photo_id}`"
              height="200px"
              class="align-end"
              cover
              @click="viewItem(item)"
              v-if="item.thumbnail_photo_id"
            >
            </v-img>
            <div 
              class="d-flex align-center justify-center bg-grey-darken-3" 
              style="height: 200px;"
              @click="viewItem(item)"
              v-else
            >
              <v-icon icon="LayoutGridFilled" rounded="circle" size="64px"></v-icon>
            </div>
            <div class="position-absolute bottom-0 left-0 w-100 pa-2" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }">
              <div class="d-flex align-center text-white">
                <div class="font-weight-bold">{{ item.name }}</div>
                <v-spacer></v-spacer>
                <v-btn icon="Trash" @click="deleteItem(item)" variant="text" rounded="circle" density="comfortable" v-if="item.status"></v-btn>
              </div>
            </div>
          </template>
        </item-grid>
        <v-pagination
          v-model="items.page"
          :length="items.total_pages"
          :total-visible="5"
          v-if="items.data.length && items.total_pages > 1"
          class="my-4"
          @update:modelValue="getItems"
        ></v-pagination>
      </template>
    </base-page>
  </div>
</template>
  
<script>
import BasePage from '@/components/BasePage.vue';
import ItemGrid from '@/components/ItemGrid.vue';
import CollectionForm from './Form.vue';
import api from '@/plugins/axios';
export default {
  name: 'Index',
  components: {BasePage, ItemGrid, CollectionForm},
  inject: ['dialog'],
  data: function(){
    return {
      items: {
        data: [],
        total: 0,
        page: 1,
        per_page: 24,
        total_pages: 0
      }
    }
  },
  computed:{
    noItems: function(){
      return !this.items.data.length;
    },
  },
  methods: {
    handleSearch(search) {
      this.getItems(1, search);
    },
    async getItems(page=1,search='') {
      let data = await api.get(`/collections/list`, { params: { page, search } });
      this.items = {...this.items,...data};
    },
    async viewItem(item) {
      this.$router.push(`/collections/${item.id}`);
    },
    async deleteItem(item) {
      this.dialog({
        title: "Remover coleção?",
        type: 'question',
        message: `Deseja realmente remover a coleção ${item.name}?`,
        showCancelButton: true,
        confirmButton: {
          text: 'Sim, Remover'
        },
        onConfirm: async () => {
          await api.delete(`/collections/delete/${item.id}`);
          this.getItems();
        }
      });
    }
  },
  mounted() {
    this.getItems();
  },
}
</script>