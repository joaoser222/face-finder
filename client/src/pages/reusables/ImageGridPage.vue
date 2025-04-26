<template>
<div class="w-100 h-100">
  <div class="d-flex flex-column align-center justify-center flex-grow-1 h-screen py-3" v-if="loading">
    <v-progress-circular class="my-6" indeterminate size="90" color="primary"></v-progress-circular>
  </div>
  <page-container v-else>
    <template #title>
      {{ title }}
    </template>
    <template #actions>
      <slot name="details-top"></slot>
      <component :is="formComponent" @success="getItems()" />
    </template>
    <template #default>
      <search-bar @search="handleSearch" v-if="search || items.data.length" @clear="search=''"></search-bar>
      <div v-if="items.data.length">
        <item-grid :items="items.data">
          <template #default="{ item }">
            <v-img
              :src="`/api/photos/thumbnail/${item[itemThumbnail]}`"
              height="200px"
              class="align-end"
              cover
              @click="selectItem(item)"
              v-if="item[itemThumbnail]"
            >
            </v-img>
            <div 
              class="d-flex flex-row align-center justify-center bg-grey-darken-3" 
              style="height: 200px;"
              @click="selectItem(item)"
              v-else
            >
              <v-icon icon="PhotoFilled" rounded="circle" size="64px"></v-icon>
            </div>
            <div class="position-absolute top-0 right-0 pa-2" :style="{ backgroundColor: 'transparent' }">
              <div class="d-flex align-center text-white">
                <slot name="item-top" :item="item"></slot>
              </div>
            </div>
            <div class="position-absolute bottom-0 left-0 w-100 pa-2" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }">
              <div class="d-flex align-center text-white">
                <slot name="item-bottom" :item="item" :deleteItem="deleteItem"></slot>
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
      </div>
      <div class="d-flex flex-column align-center justify-start w-100" v-else>
        <empty-container 
          title="Nenhum resultado encontrado"
          description="Não há itens correspondentes à sua pesquisa"
          v-if="search"
        >
          <template v-slot:banner>
            <div class="d-flex flex-column justify-center align-center">
              <v-icon icon="Search" size="100" color="primary" style="stroke-width: 1.0px"></v-icon>
            </div>
          </template>
        </empty-container>
        <empty-container
          :title="emptyTitle"
          :description="emptyDescription"
          :icon="emptyIcon"
          v-else
        ></empty-container>
      </div>
    </template>
  </page-container>
</div>
</template>

<script>
import { ref, reactive,inject, onMounted } from 'vue';
import  api  from '@/plugins/axios';
import ItemGrid from '@/components/ItemGrid.vue';
import SearchBar from './SearchBar.vue';
import EmptyContainer from './EmptyContainer.vue';
import PageContainer from '@/components/PageContainer.vue';
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    endpoint: {
      type: String,
      required: true
    },
    itemThumbnail: {
      type: String,
      default: 'thumbnail_photo_id'
    },
    emptyTitle: {
      type: String,
      default: 'Nenhum item encontrado'
    },
    emptyDescription: {
      type: String,
      default: 'Adicione novos itens para começar'
    },
    emptyIcon: {
      type: String,
      default: 'PhotoFilled'
    },
    formComponent: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  components: {
    ItemGrid,
    SearchBar,
    EmptyContainer,
    PageContainer
  },
  name: 'PhotoGrid',
  setup(props, { emit }) {
    // Estado reativo
    const catchRequestErrors = inject('catchRequestErrors');
    const dialog = inject('dialog');
    const search = ref('');

    const currentItem = ref({});
    const items = reactive({
      data: [],
      page: 1,
      total_pages: 1,
    })

    const handleSearch = (value) => {
      if(search.value != value) {
        search.value = value
        getItems();
      }
    }

    const getItems = async (page = 1) => {
      try {
        const resp = await api.get(`${props.endpoint}`, { params: { page, search: search.value } })
        Object.assign(items, resp)
      } catch (error) {
        catchRequestErrors(error)
      }
    }

    const selectItem = (item) => {
      emit('select', item);
    }

    const deleteItem = (item,type='Registro',name='item',endpoint='') => {
      dialog({
        title: `Remover ${type}?`,
        type: 'question',
        message: `Deseja realmente remover o registro ${name}?`,
        showCancelButton: true,
        confirmButton: {
          text: 'Sim, Remover'
        },
        onConfirm: async () => {
          await api.delete(endpoint)
          await getItems()
        }
      })
    }

    onMounted(() => {
      getItems();
    });

    // Retornar tudo que deve estar disponível no template
    return {
      search,
      items,
      getItems,
      selectItem,
      deleteItem,
      handleSearch
    }
  }
}
</script>