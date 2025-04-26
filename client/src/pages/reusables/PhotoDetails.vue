<template>
<v-dialog v-model="dialogDetails" @hide="emit('close')" width="800px">
  <v-card>
    <v-card-title class="border-b">Detalhes da foto {{ photo.original_name }}</v-card-title>
    <v-card-text  style="max-height: 100%; overflow-y: auto;">
      <v-img
        :src="`/api/photos/scaled/${photo.id}`"
        width="100%"
        class="align-end"
        cover
      >
      </v-img>
      <div class="mt-8" v-if="faces.length>0">
        <v-row>
          <v-col cols="12" sm="6" v-for="face in faces" :key="face.id">
            <v-card border height="100px" max-height="120px">
              <div class="d-flex flex-row flex-no-wrap align-start justify-start">
                <v-img
                  :src="`/api/photos/face-thumbnail/${face.id}`"
                  style="width: auto;height: 100px;"
                  position="left"
                ></v-img>
                <div class="flex-grow-1 text-subtitle-1 pa-1">
                  <div class="font-weight-bold">Face #{{ face.id }}</div>
                  <div class="text-caption">Idade: {{ face.data.age }}</div>
                  <div class="text-caption">Gênero: {{ face.data.gender ? 'Masculino' : 'Feminino' }}</div>
                  <div class="text-caption" v-if="face.similarity">Similaridade: {{ (face.similarity*100) }} %</div>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-card-text>
    <v-card-actions class="border-t">
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="closeDetails()">Fechar</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
</template>

<script>
import { ref,inject, watch,computed } from 'vue';
import api from '@/plugins/axios';
export default {
  name: 'PhotoDetails',
  props: {
    photo: {
      type: Object,
      required: true
    },
    searchId: {
      type: String,
      required: false
    }
  },
  setup(props,{ emit }){
    const catchRequestErrors = inject('catchRequestErrors');
    const loadingDialog = inject('loadingDialog');
    const faces = ref([]);
    const dialogDetails = ref(false);
    
    const getFaces = async () => {
      try {
        dialogDetails.value = true;
        faces.value = [];
        loadingDialog.show('Carregando faces...');
        const data = await api.get(`/photos/faces/${props.photo.id}`, {params: {search_id: props.searchId}});
        faces.value = data
      } catch (error) {
        catchRequestErrors(error);
      } finally {
        loadingDialog.hide();
      }
    }

    const closeDetails = () => {
      dialogDetails.value = false;
    }

    watch(() => props.photo, (newValue) => {
      getFaces()
    });

    return {
      dialogDetails,
      emit,
      faces,
      closeDetails
    }
  }
}
</script>

<style>

</style>