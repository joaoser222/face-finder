<template>
  <div class="h-100">
    <base-page :no-items="noItems">
      <template #title>
        Pesquisa de Face
      </template>
      <template #no-items-banner>
        <v-img src="@/assets/face_search.svg" width="350px" height="auto"></v-img>
      </template>
      <template #no-items-subtitle>
        Gerencie suas pesquisas de face
      </template>
      <template #no-items-description>
        Pesquisas são consultas em que você utiliza um rosto como 
        referência para encontrar imagens que contenham essa mesma face em diferentes coleções.
      </template>
      <template #action-buttons>
        <search-form @success="getItems()"></search-form>
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
          v-model="page"
          :length="items.total_pages"
          :total-visible="5"
          v-if="items.data.length && items.total_pages > 1"
          class="my-4"
        ></v-pagination>
      </template>
    </base-page>
  </div>
</template>
  
<script>
import BasePage from '@/components/BasePage.vue';
import ItemGrid from '@/components/ItemGrid.vue';
import SearchForm from './Form.vue';
import api from '@/plugins/axios';
export default {
  name: 'SearchIndex',
  components: {BasePage, ItemGrid, SearchForm},
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
    async getItems() {
      let data = await api.get(`/searches/list`);
      this.items = {...this.items,...data};
    },
    async viewItem(item) {
      this.$router.push(`/searches/${item.id}`);
    },
    async deleteItem(item) {
      this.dialog({
        title: "Remover pesquisa?",
        type: 'question',
        message: `Deseja realmente remover a pesquisa ${item.name}?`,
        showCancelButton: true,
        confirmButton: {
          text: 'Sim, Remover'
        },
        onConfirm: async () => {
          await api.delete(`/searches/delete/${item.id}`);
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