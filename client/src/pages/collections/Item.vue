<template>
<div>
  <base-page :no-items="noPhotos">
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
            :src="`/api/files/thumbnail/${item.id}`"
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
    </template>
  </base-page>
  <v-dialog v-model="dialogDetails" @hide="closeDetails()" width="800px">
    <v-card>
      <v-card-title>Detalhes da foto {{ selectedPhoto.original_name }}</v-card-title>
      <v-card-text>
        <v-img
          :src="`/api/files/scaled/${selectedPhoto.id}`"
          width="100%"
          height="auto"
          max-height="800px"
          class="align-end"
          cover
        >
        </v-img>
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
    showDetails(item) {
      this.selectedPhoto = item;
      this.dialogDetails = true;
    },
    closeDetails() {
      this.dialogDetails = false;
      this.selectedPhoto = {};
    },
    async getItem() {
      this.item = await api.get(`collections/show/${this.id}`);
      this.getPhotos();
    },
    async getPhotos() {
      /**
       * Carrega a lista de itens do endpoint
      */
      try {
        const data = await api.get(`collections/show-photos/${this.id}`)
        this.photos = {...data};
      } catch (error) {
        console.error('Error fetching photos:', error)
        this.$emit('error', error)
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
          await api.delete(`/collections/delete-photo/${this.id}/${item.id}`);
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