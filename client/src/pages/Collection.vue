<template>
  <Page 
    :meta="meta"
    endpoint="/collections"
    display-field="name"
    @saved="handleSaved"
    @deleted="handleDeleted"
    @error="handleError"
  >
    <!-- Slot personalizado para a lista de itens -->
    <template #items="{ items, viewItem,confirmDelete }">
      <v-row dense>
        <v-col cols="12" sm="6" md="4" lg="3" xl="2" v-for="item in items" :key="item.id">
          <v-card height="200px" border="sm" >
            <v-img
              :src="`https://picsum.photos/500/300?random=${n}`"
              height="200px"
              class="align-end"
              cover
              @click="viewItem(item,$event)"
            >
            </v-img>
            <div class="position-absolute bottom-0 left-0 w-100 pa-2" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }">
              <div class="d-flex align-center text-white">
                <div class="font-weight-bold">{{ item.name }}</div>
                <v-spacer></v-spacer>
                <v-btn icon="Trash" @click="confirmDelete(item)" variant="text" rounded="circle" density="comfortable"></v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </template>
    <!-- Slot personalizado para o formulário -->
    <template #form="{ setFormStatus,item }">
      <v-form v-model="formStatus" @update:modelValue="setFormStatus">
        <v-text-field
          v-model="item.name"
          label="Nome"
          :rules="[validations.required]"
          outlined
          dense
          class="mb-3"
        />
      </v-form>
    </template>
  </Page>
</template>

<script>
import validations from '@/plugins/validations';
export default {
  data() {
    return {
      // Meta informações
      meta: {
        subtitle: 'Gerencie suas coleções de fotos',
        description: 'Coleções são grupos de fotos que você deve criar para utilizar o algoritmo de pesquisa',
        singular: 'Coleção',
        plural: 'Coleções',
        image: new URL('@/assets/collections.svg', import.meta.url).href
      },
      formStatus: false,
    };
  },
  computed: {
    validations() {
      return validations;
    }
  },
  methods: {
    // Funções de callback
    handleSaved(item) {
      console.log('Item salvo:', item);
    },

    handleDeleted(item) {
      console.log('Item excluído:', item);
    },

    handleError(error) {
      console.error('Erro:', error);
    }
  }
};
</script>