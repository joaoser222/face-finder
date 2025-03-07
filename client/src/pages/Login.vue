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
            <DataForm
              ref="formRef"
              :items="currentFields"
              :errors="formErrors"
              @update="handleFormUpdate"
              density="comfortable"
              class="pa-0"
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
              @click="handleSubmit"
            >
              {{ isLogin ? 'Entrar' : 'Criar conta' }}
            </v-btn>

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

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import DataForm from '@/components/DataForm.vue'

const router = useRouter()
const isLogin = ref(true)
const loading = ref(false)
const formRef = ref(null)
const formData = ref({})
const formStatus = ref(false)
const formErrors = ref({})

// Campos do formulário de login
const loginFields = [
  {
    name: 'email',
    label: 'Email',
    component: 'text',
    type: 'email',
    validation: 'required|email',
    prependInnerIcon: 'Mail',
    colProps: { cols: 12 }
  },
  {
    name: 'password',
    label: 'Senha',
    component: 'password',
    validation: 'required|min:6',
    prependInnerIcon: 'Lock',
    colProps: { cols: 12 }
  }
]

// Campos adicionais para o cadastro
const registerFields = [
  {
    name: 'name',
    label: 'Nome completo',
    component: 'text',
    validation: 'required',
    fieldProps: {
      'prepend-inner-icon': 'User',
      'bg-color': 'grey-lighten-4'
    },
    colProps: { cols: 12 }
  },
  {
    name: 'username',
    label: 'Nome de usuário',
    component: 'text',
    validation: 'required',
    prependInnerIcon: 'UserCircle',
    colProps: { cols: 12 }
  },
  ...loginFields,
  {
    name: 'confirmPassword',
    label: 'Confirmar senha',
    component: 'password',
    validation: 'required|same:password',
    prependInnerIcon: 'Lock',
    colProps: { cols: 12 }
  }
]

// Campos atuais baseados no modo
const currentFields = computed(() => isLogin.value ? loginFields : registerFields)

const handleFormUpdate = ({ form, status }) => {
  console.log('handleFormUpdate', form, status);
  formData.value = form
  formStatus.value = status
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  formData.value = {}
  formErrors.value = {}
}

const handleSubmit = async () => {
  if (!formStatus.value) return

  loading.value = true
  formErrors.value = {}

  try {
    if (isLogin.value) {
      // Lógica de login
      console.log('Login:', {
        email: formData.value.email,
        password: formData.value.password
      })
      // await loginUser(formData.value)
    } else {
      // Lógica de cadastro
      console.log('Cadastro:', formData.value)
      // await registerUser(formData.value)
    }
    router.push('/')
  } catch (error) {
    console.error('Error:', error)
    if (error.response?.data?.errors) {
      formErrors.value = error.response.data.errors
    }
  } finally {
    loading.value = false
  }
}
</script>