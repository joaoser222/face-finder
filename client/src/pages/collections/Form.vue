<template>
  <dialog-form @save="save" :content="content" :multipart-form="true">
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
      />
      <v-file-input
        v-model="form.file"
        label="Arquivo"
        accept=".zip"
        placeholder="Arquivo no formato ZIP"
        :rules="[
          (v) => (id?null:validations.required(v))
        ]"
        dense
        class="mb-3"
      ></v-file-input>
      <div class="text-caption">
        **O arquivo deve estar no formato ZIP e conter apenas imagens no formato PNG ou JPG. Arquivos em outros formatos serão ignorados.
      </div>
    </template>
  </dialog-form>
</template>

<script>
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
import DialogForm from '@/components/DialogForm.vue';
import api from '@/plugins/axios';
export default {
  name: 'CollectionForm',
  props: {
    id: {
      type: Number,
      required: false
    },
    content: {
      type: Object,
      required: false
    }
  },
  inject: ['dialog'],
  components: {DialogForm},
  data: function(){
    return {
      item: {
        name: '',
        file: null
      }
    }
  },
  computed: {
    actionName() {
      return this.id ? 'Editar Coleção' : 'Criar Coleção';
    },
    validations() {
      return validations;
    },
    masks() {
      return masks;
    }
  },
  methods: {
    async save(data) {
      try {
        if(this.id) {
          await api.put(`/collections/update/${this.id}`, data, {headers: {'Content-Type': 'multipart/form-data'}});
        } else {
          await api.post(`/collections/create`, data, {headers: {'Content-Type': 'multipart/form-data'}});
        }
        this.$emit('success');
      } catch (error) {
        this.dialog({title: "Erro!", type: 'error',message: error});
      }
    }
  }
}
</script>