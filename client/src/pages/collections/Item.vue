<template>
  <div class="d-flex flex-column align-start justify-center flex-grow-1">
    <image-grid-page
      :title="`Coleção: ${itemDetails.name}`"
      :endpoint="`/photos/by-owner/collection/${id}`"
      @select="selectItem"
      :item-thumbnail="'id'"
      :loading="loading"
      v-bind="getEmptyData(itemDetails.status)"
    >
      <template #actions="{getItems}">
        <component :is="CollectionForm" @success="getItems()" />
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
    <photo-details :photo="selectedPhoto"></photo-details>
  </div>
</template>

<script>
import { ref,inject,onMounted,computed } from 'vue';
import { useRouter } from 'vue-router';
import ImageGridPage from '../reusables/ImageGridPage.vue';
import CollectionForm from './Form.vue';
import PhotoDetails from '../reusables/PhotoDetails.vue';
import api from '@/plugins/axios';
import statusOptions from './statusOptions';

export default {
  name: 'CollectionItem',
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
    const itemDetails = ref({});
    const loading = ref(true);
    const catchRequestErrors = inject('catchRequestErrors');

    const selectItem = (item) => {
      selectedPhoto.value = {...item};
    }

    const getItemDetails = async (page = 1) => {
      try {
        const resp = await api.get(`collections/show/${props.id}`)
        itemDetails.value = resp;
      } catch (error) {
        catchRequestErrors(error)
      } finally {
        loading.value = false;
      }
    }

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
      selectedPhoto,
      itemDetails,
      statusOptions,
      CollectionForm,
      selectItem,
      getEmptyData
    }
  }
}
</script>