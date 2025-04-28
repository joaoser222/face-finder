<template>
  <dialog-form @save="save" :content="content" :multipart-form="true" @close="close">
    <template #title>
      {{actionName}}
    </template>
    <template #form-fields="{ form }">
      <v-text-field
        v-model="form.name"
        label="Nome"
        :rules="[validations.required]"
        dense
        placeholder="Nome da pesquisa"
        class="mb-3"
        v-maska="masks.uppercase"
        v-if="!itemId"
      />
      <search-collection 
        @update:selected="form.collections = $event" 
        :rules="[validations.minLength(1,'coleção')]"
        class="mb-3"
        v-if="!itemId"
      />
      <div class="mb-5">
        <v-label>Nível de tolerância</v-label>
        <v-slider
          v-model="form.tolerance_level"
          :max="90"
          :min="10"
          :step="5"
          thumb-label
          :rules="[validations.required]"
          persistent-hint
          :hint="'**A tolerância serve para medir o mínimo de semelhança tolerável entre as faces. Quanto menor o nível maior a chance de falso positivo'"
        ></v-slider>
      </div>
      <div class="mb-5" v-if="itemId">
        <v-checkbox 
          v-model="form.force_recreate" 
          label="Forçar recriação de registros"
          persistent-hint
          :hint="'**Remove os resultados encontrados e cria novamente com os novos parâmetros'"
        />
      </div>
      <v-file-input
        v-model="form.file"
        label="Arquivo"
        placeholder="Arquivo no formato ZIP"
        accept="image/png, image/jpeg"
        :rules="[validations.required]"
        dense
        class="mb-3"
        persistent-hint
        :hint="'**O arquivo deve ser uma imagem no formato PNG ou JPG'"
        v-if="!itemId"
      ></v-file-input>
    </template>
  </dialog-form>
</template>

<script>
import { ref, computed, inject} from 'vue';
import { useRoute } from 'vue-router';
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
import DialogForm from '@/components/DialogForm.vue';
import api from '@/plugins/axios';
import SearchCollection from '@/pages/searches/SearchCollection.vue';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'SearchForm',
  components: { DialogForm, SearchCollection },
  setup(props, { emit }) {
    const route = useRoute();
    const catchRequestErrors = inject('catchRequestErrors');
    const loadingDialog = inject('loadingDialog');
    const dialog = inject('dialog');
    const authStore = useAuthStore();

    const content = ref({
      name: '',
      file: null,
      tolerance_level: authStore.user.tolerance_level,
      collections: []
    });

    const itemId = computed(() => route.params.id);
    const actionName = computed(() => itemId.value ? 'Reexecutar' : 'Criar Pesquisa');

    const close = (updateForm)=>{
      // Preserva o valor de tolerancia do usuário reset do form
      updateForm({tolerance_level: authStore.user.tolerance_level});
    }

    const save = async (data) => {
      
      if (itemId.value) {
        await executeUpdate(data);
      } else {
        await create(data);
      }
    };

    const create = async (data) => {
      try {
        loadingDialog.show('Salvando Pesquisa');
        await api.post(`/searches/create`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
        emit('success');
      } catch (error) {
        catchRequestErrors(error);
      } finally {
        loadingDialog.hide();
      }
    };

    const executeUpdate = (formData) => {
      let data = JSON.parse(formData.get('params'));
      const _request = () => {
        loadingDialog.show('Enviando atualização de pesquisa');
        api.put(`searches/update/${itemId.value}`, data)
          .catch((err) => catchRequestErrors(err))
          .finally(() => loadingDialog.hide());
      };

      if (data.force_recreate) {
        dialog({
          title: 'Deseja recriar?',
          message: `Se fizer isso todos os registros de fotos vinculados serão removidos para a nova pesquisa`,
          type: 'warning',
          showCancelButton: true,
          cancelButton: {
            text: 'Não recriar',
          },
          confirmButton: {
            text: 'Sim, desejo recriar',
          },
          onConfirm: () => _request(),
          onCancel: () => {
            data.force_recreate = false;
            _request();
          },
        });
      }else{
        _request();
      }
    };

    return {
      content,
      itemId,
      actionName,
      validations,
      masks,
      save,
      close,
      create,
      executeUpdate
    };
  }
};
</script>