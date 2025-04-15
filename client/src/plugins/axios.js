import axios from 'axios'

// Criando uma instância do axios com configurações personalizadas
const api = axios.create({
  baseURL: '/api', // Adiciona o prefixo /api a todas as requisições
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Interceptor para requisições
api.interceptors.request.use(
  (config) => {
    // Pega o token do localStorage (se existir)
    const auth = localStorage.getItem('auth')

    if (auth) {
      const { token, expiresAt } = JSON.parse(auth);
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para respostas
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      // O servidor respondeu com um status de erro
      if (error.response.status === 401) {
        // Token expirado ou inválido
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api 