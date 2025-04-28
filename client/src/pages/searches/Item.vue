<template>
  <div class="d-flex flex-column align-start justify-center flex-grow-1">
    <image-grid-page
      :title="`Pesquisa de Face: ${itemDetails.name}`"
      :endpoint="`/photos/by-owner/search/${id}`"
      delete-endpoint="/photos/delete"
      :form-component="SearchForm"
      @select="selectItem"
      :item-label="'original_name'"
      :item-thumbnail="'id'"
      :loading="loading"
      v-bind="getEmptyData(itemDetails.status)"
    >
      <template #details-top >
        <v-card width="200px" class="mx-auto">
          <v-img
            :src="`/api/photos/thumbnail/${itemDetails['thumbnail_photo_id']}`"
            height="auto"
            max-width="200px"
            class="align-end"
            cover
            v-tooltip="'Face de referência da pesquisa'"
          ></v-img>
        </v-card>
      </template>
      <template #actions="{getItems,hasItems}">
        <div class="d-flex flex-row align-end justify-center">
          <v-btn text="Baixar resultados" color="primary" class="mt-4 mr-2" @click="downloadResults" v-if="hasItems"></v-btn>
          <component :is="SearchForm" @success="getItems()"></component>
        </div>
      </template>
      <template #item-top>
        <v-btn 
          :icon="statusOptions[itemDetails.status].icon" 
          variant="text" 
          rounded="circle" 
          density="comfortable" 
          v-tooltip="statusOptions[itemDetails.status].title" 
        >
        </v-btn>
      </template>
      <template #item-bottom="{item,deleteItem}">
        <div class="font-weight-bold text-truncate">{{ item.original_name }}</div>
        <v-spacer></v-spacer>
        <v-btn 
          icon="Trash"
          @click="deleteItem(item,'Foto',item.original_name,`/photos/delete/${item.id}`)"
          variant="text" rounded="circle" density="comfortable" 
          v-if="statusOptions[itemDetails.status].showDelete"
        >
        </v-btn>
      </template>
    </image-grid-page>
    <photo-details :photo="selectedPhoto" :search-id="id"></photo-details>
  </div>
</template>

<script>
import { ref,onMounted,inject,computed} from 'vue';
import ImageGridPage from '../reusables/ImageGridPage.vue';
import SearchForm from './Form.vue';
import PhotoDetails from '../reusables/PhotoDetails.vue';
import api from '@/plugins/axios';
import statusOptions from './statusOptions';

export default {
  name: 'SearchItem',
  props:{
    id: {
      type: String,
      required: true
    }
  },
  components: {
    ImageGridPage,
    PhotoDetails
  },
  setup(props) {
    const selectedPhoto = ref({});
    const loading = ref(true);
    const itemDetails = ref({});
    const catchRequestErrors = inject('catchRequestErrors');
    const loadingDialog = inject('loadingDialog');
    const formatBytes = inject('formatBytes');
    
    const selectItem = (item) => {
      selectedPhoto.value = {...item};
    }

    const getItemDetails = async (page = 1) => {
      try {
        const resp = await api.get(`searches/show/${props.id}`)
        itemDetails.value = resp;
      } catch (error) {
        catchRequestErrors(error)
      } finally {
        loading.value = false;
      }
    }

    const downloadResults = async () => {
      try {
        const response = await api.get(`/searches/download/${props.id}`, {
          responseType: 'blob', 
          onDownloadProgress: (progressEvent) => {
            let bytesLoaded = formatBytes(progressEvent.loaded);
            loadingDialog.show(`Baixando resultados ${bytesLoaded}`);
          },
        });

        // Extrai o nome do arquivo do header (ou usa um fallback)
        const contentDisposition = response.headers['content-disposition'];
        const fileName = contentDisposition?.match(/filename=["']?(.+?)["']?$/i)?.[1] || 'results.zip';

        // Cria um link temporário para download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();

        // Limpeza
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);

      } catch (error) {
        console.error('Erro no download:', error);
      }finally {
        loadingDialog.hide();
      }
    };

    const getEmptyData = (status=0)=>{
      let statusData = statusOptions[status];
      return {
        emptyDescription: statusData.description,
        emptyTitle: statusData.title,
        emptyIcon: statusData.icon
      }
    }

    onMounted(()=>{
      getItemDetails()
    })

    return {
      loading,
      itemDetails,
      statusOptions,
      getEmptyData,
      downloadResults,
      selectedPhoto,
      SearchForm,
      selectItem
    }
  }
}
</script>