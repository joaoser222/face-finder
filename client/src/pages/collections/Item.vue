<template>
<div>
  <base-page 
    :no-items="noPhotos" 
    @search="handleSearch"
  >
    <template #title>
      Coleção: {{ item.name }}
    </template>
    <template #no-items-banner>
      <v-img src="@/assets/collections.svg" width="350px" height="auto"></v-img>
    </template>
    <template #no-items-subtitle>
      Processando imagens
    </template>
    <template #no-items-description>
      Aguarde a finalização do processo para ver as imagens
    </template>
    <template #action-buttons>
      <collection-form @success="getItem()" :id="id" :content="item"></collection-form>
    </template>
    <template #default>
      <item-grid :items="photos.data">
        <template #default="{ item }">
          <v-img
            :src="`/api/photos/thumbnail/${item.id}`"
            height="200px"
            class="align-end"
            cover
            @click="showDetails(item)"
          >
          </v-img>
          <div class="position-absolute bottom-0 left-0 w-100 pa-2" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }">
            <div class="d-flex align-center text-white">
              <div class="font-weight-bold text-truncate">{{ item.original_name }}</div>
              <v-spacer></v-spacer>
              <v-btn icon="Trash" @click="deletePhoto(item)" variant="text" rounded="circle" density="comfortable"></v-btn>
            </div>
          </div>
        </template>
      </item-grid>
      <v-pagination
        v-model="photos.page"
        :length="photos.total_pages"
        :total-visible="5"
        v-if="photos.data.length && photos.total_pages > 1"
        class="my-4"
        @update:modelValue="getPhotos"
      ></v-pagination>
    </template>
  </base-page>
  <v-dialog v-model="dialogDetails" @hide="closeDetails()" width="800px">
    <v-card v-if="Object.keys(selectedPhoto).length">
      <v-card-title>Detalhes da foto {{ selectedPhoto.original_name }}</v-card-title>
      <v-card-text>
        <v-img
          :src="`/api/photos/scaled/${selectedPhoto.id}`"
          width="100%"
          height="auto"
          class="align-end"
          cover
        >
        </v-img>
        <div class="mt-8" v-if="selectedPhoto.faces.data.length">
          <v-row>
            <v-col cols="12" sm="6" v-for="face in selectedPhoto.faces.data" :key="face.id">
              <v-card border height="100px" max-height="120px">
                <div class="d-flex flex-row flex-no-wrap align-start justify-start">
                  <v-img
                    :src="`/api/photos/face-thumbnail/${face.id}`"
                    style="width: auto;height: 100px;"
                    position="left"
                  ></v-img>
                  <div class="flex-grow-1 text-subtitle-1 pa-3">
                    <div class="font-weight-bold">Face #{{ face.id }}</div>
                    <div class="text-caption">Idade: {{ face.data.age }}</div>
                    <div class="text-caption">Gênero: {{ face.data.gender ? 'Masculino' : 'Feminino' }}</div>
                  </div>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="closeDetails()">Fechar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</div>
</template>
  
<script>
import BasePage from '@/components/BasePage.vue';
import ItemGrid from '@/components/ItemGrid.vue';
import CollectionForm from './Form.vue';
import api from '@/plugins/axios';
export default {
  name: 'CollectionItem',
  props:{
    id: {
      type: Number,
      required: true
    }
  },
  inject: ['dialog'],
  components: {BasePage, ItemGrid, CollectionForm},
  data: function(){
    return {
      item: {},
      dialogDetails: false,
      selectedPhoto: {},
      photos: {
        data: []
      },
    }
  },
  computed:{
    noPhotos: function(){
      return !this.photos.data.length;
    }
  },
  methods: {
    async showDetails(item) {
      this.selectedPhoto = {...item};
      this.dialogDetails = true;
      this.getFaces();
    },
    closeDetails() {
      this.dialogDetails = false;
      this.selectedPhoto = {};
    },
    async getItem() {
      this.item = await api.get(`collections/show/${this.id}`);
      this.getPhotos();
    },
    handleSearch(search) {
      this.getPhotos(1, search);
    },
    async getPhotos(page=1,search='') {
      /**
       * Carrega a lista de itens do endpoint
      */
      try {
        const data = await api.get(`/photos/by-owner/collection/${this.id}`, { params: { page, search } })
        this.photos = {...data};
      } catch (error) {
        console.error('Error fetching photos:', error)
        this.$emit('error', error)
      }
    },
    async getFaces() {
      /**
       * Carrega a lista de faces do endpoint
      */
      try {
        this.selectedPhoto.faces = {loading: true, data: []};
        this.selectedPhoto.faces.data = await api.get(`/photos/faces/${this.selectedPhoto.id}`)
      } catch (error) {
        console.error('Error fetching faces:', error)
      } finally {
        this.selectedPhoto.faces.loading = false;
      }
    },
    async deletePhoto(item) {
      this.dialog({
        title: "Remover foto?",
        type: 'question',
        message: `Deseja realmente remover a foto ${item.original_name}?`,
        showCancelButton: true,
        confirmButton: {
          text: 'Sim, Remover'
        },
        onConfirm: async () => {
          await api.delete(`/photos/delete/${item.id}`);
          this.getPhotos();
        }
      });
    }
  },
  mounted() {
    this.getItem();
  },
}
</script>