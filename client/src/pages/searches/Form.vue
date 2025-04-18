<template>
  <dialog-form @save="save" :content="content" :multipart-form="true">
    <template #title>
      Criar Pesquisa
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
      />
      <search-collection 
        @update:selected="form.collections = $event" 
        :rules="[validations.minLength(1,'coleção')]"
        class="mb-3"
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
      ></v-file-input>
    </template>
  </dialog-form>
</template>

<script>
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
import DialogForm from '@/components/DialogForm.vue';
import api from '@/plugins/axios';
import SearchCollection from '@/pages/searches/SearchCollection.vue';
export default {
  name: 'SearchForm',
  props: {
    id: {
      type: Number,
      required: false
    },
  },
  inject: ['catchRequestErrors','loadingDialog'],
  components: {DialogForm, SearchCollection},
  data: function(){
    return {
      content: {
        name: '',
        file: null,
        tolerance_level: 60,
        collections: []
      }
    }
  },
  computed: {
    validations() {
      return validations;
    },
    masks() {
      return masks;
    }
  },
  methods: {
    async save(data) {
      this.loadingDialog.show('Salvando Pesquisa');
      try {
        await api.post(`/searches/create`, data, {headers: {'Content-Type': 'multipart/form-data'}});
        this.$emit('success');
      } catch (error) {
        this.catchRequestErrors(error);
      } finally {
        this.loadingDialog.hide();
      }
    }
  }
}
</script>