<template>
<div>
  <v-btn color="primary" variant="flat" @click="open()">
    <slot name="title"></slot>
  </v-btn>
  <v-dialog v-model="dialogStatus" max-width="500px">
    <v-card>
      <v-card-title>
        <slot name="title"></slot>
      </v-card-title>

      <v-card-text>
        <v-form v-model="formStatus">
          <slot name="form-fields" :form="form" :setFormStatus="setFormStatus"></slot>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey-darken-1" @click="close()">
          Cancelar
        </v-btn>
        <v-btn 
          color="primary" 
          @click="sendData()" 
          :disabled="!formStatus"
        >
          Salvar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</div>
</template>

<script>
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
export default {
  name: 'CollectionForm',
  props: {
    id: {
      type: Number,
      required: false
    },
    multipartForm:{
      type: Boolean,
      default: false
    },
    content: {
      type: Object,
      required: false
    }
  },
  data: function(){
    return {
      dialogStatus: false,
      formStatus: false,
      form: {}
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
  watch: {
    content: {
      handler() {
        this.form = {...this.content};
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    open() {
      this.dialogStatus = true;
    },
    close() {
      this.dialogStatus = false;
      this.form = {};
      this.$emit('close');
    },
    getFormData(){
      if(this.multipartForm){
        const formData = new FormData();

        const { file, ...params } = this.form;

        if(file) formData.append('file', this.form.file);

        formData.append('params', JSON.stringify(params));
                
        return formData
      }else{
        return {...this.form};
      }
    },
    sendData() {
      let data = this.getFormData();
      this.close();
      this.$emit('save', data);
    },
    setFormStatus(value) {
      this.formStatus = value;
    }
  }
}
</script>