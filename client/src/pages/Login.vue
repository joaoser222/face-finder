<template>
  <v-container fluid class="fill-height bg-grey-lighten-4">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-8">
          <!-- Logo -->
          <div class="d-flex flex-column align-center mb-6">
            <v-img src="@/assets/logo.svg" width="64px" height="64px" class="mb-2"/>
            <h1 class="text-h5 font-weight-medium text-grey-darken-3">
              Face Finder
            </h1>
          </div>

          <!-- Card Header -->
          <v-card-title class="text-center px-0 pb-6">
            <h2 class="text-h4 font-weight-medium text-grey-darken-3">
              {{ isLogin ? 'Bem-vindo de volta' : 'Criar conta' }}
            </h2>
            <span class="text-body-1 text-grey-darken-1 mt-2">
              {{ isLogin ? 'Entre com suas credenciais' : 'Preencha seus dados para começar' }}
            </span>
          </v-card-title>

          <v-card-text class="px-0">
            <!-- Formulário de Login/Cadastro -->
            <v-form ref="form" v-model="formStatus" @submit.prevent="handleSubmit">

              <!-- Campo de Nome de Usuário (apenas para cadastro) -->
              <v-text-field
                v-if="!isLogin"
                v-model="form.username"
                label="Nome de usuário"
                :rules="[
                  validations.required
                ]"
                prepend-inner-icon="mdi-account-circle"
                outlined
                dense
                class="mb-4"
              />
              
              <!-- Campo de Email -->
              <v-text-field
                v-model="form.email"
                label="Email"
                type="email"
                :rules="[
                  validations.required,
                  validations.email
                ]"
                prepend-inner-icon="mdi-email"
                outlined
                dense
                class="mb-4"
              />

              <!-- Campo de Senha -->
              <v-password-input
                v-model="form.password"
                label="Senha"
                type="password"
                :rules="[
                  validations.required,
                  validations.minLength(6)
                ]"
                prepend-inner-icon="mdi-lock"
                outlined
                dense
                class="mb-4"
              />

              <!-- Campo de Confirmar Senha (apenas para cadastro) -->
              <v-password-input
                v-if="!isLogin"
                v-model="form.password_confirmation"
                label="Confirmar senha"
                type="password"
                :rules="[
                  validations.required,
                  v => validations.sameAs(v,form.password)
                ]"
                prepend-inner-icon="mdi-lock"
                outlined
                dense
                class="mb-4"
              />

              <!-- Botão de Submit -->
              <v-btn
                type="submit"
                color="black"
                block
                size="large"
                :loading="loading"
                :disabled="!formStatus"
                class="mt-6 mb-4"
                elevation="0"
              >
                {{ isLogin ? 'Entrar' : 'Criar conta' }}
              </v-btn>
            </v-form>

            <!-- Link para alternar -->
            <div class="text-center">
              <a 
                href="#" 
                @click.prevent="toggleMode" 
                class="text-decoration-none text-primary"
              >
                {{ isLogin ? 'Ainda não tem conta? Cadastre-se' : 'Já possui conta? Faça login' }}
              </a>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { validations } from '@/plugins/validator';
import VPasswordInput from '@/components/VPasswordInput.vue';
import api from '@/plugins/axios';
import { useAuthStore } from '@/stores/authStore'; // Importe a store

export default {
  name: 'Login',
  components: {
    VPasswordInput
  },
  data() {
    return {
      isLogin: true,
      loading: false,
      formStatus: false,
      form: {
        email: '',
        password: '',
        username: '',
        password_confirmation: ''
      },
      errors: {}
    }
  },
  computed: {
    validations() {
      return validations;
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.$refs.form.reset() // Reseta o formulário ao alternar o modo
      this.errors = {}
    },
    async handleSubmit() {
      if (!this.formStatus) return;

      this.loading = true;
      this.errors = {};

      try {
        const authStore = useAuthStore(); 

        let postData = {
          url: '/auth/login',
          data: {
            email: this.form.email,
            password: this.form.password
          }
        };

        if (!this.isLogin) {
          postData = {
            url: '/auth/register',
            data: {...this.form}
          }
        } 

        const data = await api.post(postData.url,postData.data);
        authStore.setAuth(data.token, data.expires_at);
        
        this.$router.push('/dashboard');

      } catch (error) {
        console.error('Error:', error);
        if (error.response?.data?.errors) {
          this.errors = error.response.data.errors;
        }
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>