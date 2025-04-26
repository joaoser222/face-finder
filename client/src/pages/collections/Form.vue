<template>
  <dialog-form @save="save" :content="item" :multipart-form="true">
    <template #title>
      {{ actionName }}
    </template>
    <template #form-fields="{ form }">
      <v-text-field
        v-model="form.name"
        label="Nome"
        :rules="[validations.required]"
        dense
        placeholder="Nome da coleção"
        class="mb-3"
        v-maska="masks.uppercase"
        v-if="!itemId"
      />
      <v-file-input
        v-model="form.file"
        label="Arquivo"
        accept=".zip"
        placeholder="Arquivo no formato ZIP"
        :rules="[validations.required]"
        dense
        class="mb-3"
        persistent-hint
        :hint="'**O arquivo deve estar no formato ZIP e conter apenas imagens no formato PNG ou JPG. Arquivos em outros formatos serão ignorados.'"
      ></v-file-input>
    </template>
  </dialog-form>
</template>

<script>
import { ref, computed, inject } from 'vue';
import { useRoute } from 'vue-router';
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
import DialogForm from '@/components/DialogForm.vue';
import api from '@/plugins/axios';

export default {
  name: 'CollectionForm',
  props:{
    id: {
      type: String,
      required: true
    }
  },
  components: { DialogForm },
  setup(props, { emit }) {
    const route = useRoute();
    const loadingDialog = inject('loadingDialog');
    const catchRequestErrors = inject('catchRequestErrors');

    const item = ref({
      name: '',
      file: null
    });

    const itemId = computed(() => route.params.id);
    const actionName = computed(() => itemId.value ? 'Atualizar Coleção' : 'Criar Coleção');

    const save = async (data) => {
      loadingDialog.show('Salvando Coleção');
      try {
        if (itemId.value) {
          await api.put(`/collections/update/${itemId.value}`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
        } else {
          await api.post(`/collections/create`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
        }
        emit('success');
      } catch (error) {
        catchRequestErrors(error);
      } finally {
        loadingDialog.hide();
      }
    };

    return {
      item,
      itemId,
      actionName,
      validations,
      masks,
      save
    };
  }
};
</script>