<template>
  <page-container>
    <template #title>
      Configurações
    </template>
    <template #default>
      <v-form v-model="formStatus">
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.username"
              label="Nome"
              :rules="[validations.required]"
              dense
              placeholder="Nome de usuário"
              class="mb-3"
              v-maska="masks.uppercase"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.email"
              label="Email"
              :rules="[validations.required]"
              dense
              placeholder="Email do usuário"
              class="mb-3"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-label>Nível de tolerância padrão</v-label>
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
          </v-col>
          <v-col cols="12" class="d-flex justify-end">
            <v-btn color="grey" text="Voltar" class="mr-2" @click="$router.push('/')"></v-btn>
            <v-btn color="primary" text="Salvar" @click="sendForm()" :disabled="!formStatus"></v-btn>
          </v-col>
        </v-row>
      </v-form>
    </template>
  </page-container>
</template>

<script>
import PageContainer from '@/components/PageContainer.vue';
import validations from '@/plugins/validations';
import masks from '@/plugins/masks';
import api from '@/plugins/axios';
import { useAuthStore } from '@/stores/authStore';
import { fi } from 'vuetify/locale';
export default {
  name: 'Setting',
  components: {
    PageContainer
  },
  inject: ['catchRequestErrors','loadingDialog','dialog'],
  data() {
    return {
      form: {
        name: '',
        email: '',
        tolerance_level: 0
      },
      formStatus: false
    }
  },
  computed:{
    validations: ()=>validations,
    masks: ()=>masks,
  },
  methods:{
    async sendForm(){
      try {
        this.loadingDialog.show('Enviando dados do usuário');
        const data = await api.post(`/auth/update`,this.form);
        const authStore = useAuthStore();
        authStore.setUser(this.form);
        this.dialog({
          title: 'Sucesso',
          message: 'Dados atualizados com sucesso!',
          type: 'success'
        });
      }catch (error) {
        this.catchRequestErrors(error);
      }finally{
        this.loadingDialog.hide();
      }
    },
    async getItem(){
      try {
        const data = await api.get(`/auth/session`);
        this.form = data;
      }catch (error) {
        this.catchRequestErrors(error);
      }
    }
  },
  mounted(){
    this.getItem();
  }
}
</script>

<style>

</style>