<template>
  <div class="h-100">
    <base-page 
      :no-items="noPhotos" 
      @search="handleSearch"
    >
      <template #title>
        Pesquisa: {{ item.name }}
      </template>
      <template #no-items-banner>
        <v-img src="@/assets/face_search.svg" width="350px" height="auto"></v-img>
      </template>
      <template #no-items-subtitle>
        Processando imagens
      </template>
      <template #no-items-description>
        Aguarde a finalização do processo para ver as imagens
      </template>
      <template #action-buttons>
        <v-btn
          color="primary"
          class="mr-2"
          variant="flat"
          @click="openExecutionUpdate()"
        >
          Reexecutar
        </v-btn>
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
    <v-dialog v-model="execution.dialog" max-width="500px">
      <v-card>
        <v-card-title>Dados para a nova execução</v-card-title>
        <v-card-text>
          <div class="mb-5">
            <v-label>Nível de tolerância</v-label>
            <v-slider
              v-model="execution.form.tolerance_level"
              :max="90"
              :min="10"
              :step="5"
              thumb-label
              persistent-hint
              :hint="'**A tolerância serve para medir o mínimo de semelhança tolerável entre as faces. Quanto menor o nível maior a chance de falso positivo'"
            ></v-slider>
          </div>
          <div class="mb-5">
            <v-checkbox 
              v-model="execution.form.force_recreate" 
              label="Forçar recriação de registros"
              persistent-hint
              :hint="'**Remove os resultados encontrados e cria novamente com os novos parâmetros'"
            />
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="executeUpdate()">Atualizar</v-btn>
          <v-btn color="gray" @click="execution.dialog = false">Cancelar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
  </template>
    
  <script>
  import BasePage from '@/components/BasePage.vue';
  import ItemGrid from '@/components/ItemGrid.vue';
  import SearchForm from './Form.vue';
  import api from '@/plugins/axios';
  export default {
    name: 'SearchItem',
    props:{
      id: {
        type: Number,
        required: true
      }
    },
    inject: ['dialog','catchRequestErrors','loadingDialog'],
    components: {BasePage, ItemGrid, SearchForm},
    data: function(){
      return {
        item: {},
        dialogDetails: false,
        execution: {
          dialog: false,
          form: {
            tolerance_level: 0,
            force_recreate: 0
          }
        },
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
      openExecutionUpdate(){
        this.execution.form.tolerance_level = this.item.tolerance_level;
        this.execution.dialog = true;
      },
      executeUpdate(){
        let _request = ()=>{
          this.execution.dialog = false;
          this.loadingDialog.show('Enviando atualização de pesquisa');
          api.put(`searches/update/${this.id}`,this.execution.form)
          .then((resp)=>{
            if(this.execution.form.force_recreate) location.reload();
          })
          .catch((err)=>this.catchRequestErrors(err))
          .finally(()=>this.loadingDialog.hide());
        };

        if(this.execution.form.force_recreate){
          this.dialog({
            title: 'Deseja recriar?',
            message: `Se fizer isso todos os registros de fotos vinculados serão removidos para a nova pesquisa`,
            type: 'warning',
            onConfirm: ()=>_request(),
            onCancel: ()=>{
              this.execution.form.force_recreate = false;
              _request();
            },
          });
        }
      },
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
        this.item = await api.get(`searches/show/${this.id}`);
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
          const data = await api.get(`/photos/by-search-face/${this.id}`, { params: { page, search } })
          this.photos = {...data};
        } catch (error) {
          this.catchRequestErrors(error);
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
          this.catchRequestErrors(error);
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