<template>
  <Page 
    :meta="meta"
    endpoint="/collections"
    display-field="name"
    @saved="handleSaved"
    @deleted="handleDeleted"
    @error="handleError"
  >
    <!-- Slot personalizado para o formulário -->
    <template #form="{ setForm }">
      <v-form v-model="isFormValid" @update:modelValue="setForm(form, $event)">
        <v-text-field
          v-model="form.name"
          label="Nome"
          :rules="[required]"
          outlined
          dense
          class="mb-3"
        />
        <v-textarea
          v-model="form.description"
          label="Descrição"
          outlined
          dense
        />
      </v-form>
    </template>
  </Page>
</template>

<script>
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

      // Estado para controlar a validação do formulário
      isFormValid: false,

      // Dados do formulário
      form: {
        name: '',
        description: ''
      }
    };
  },
  methods: {
    // Regra de validação
    required(value) {
      return !!value || 'Campo obrigatório.';
    },

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