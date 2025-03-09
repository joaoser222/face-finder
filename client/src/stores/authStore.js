import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,       // Armazena o token JWT
    expiresAt: null,   // Armazena o tempo de expiração do token
  }),
  actions: {
    // Define o token e o tempo de expiração
    setAuth(token, expiresAt) {
      this.token = token;
      this.expiresAt = expiresAt;
    },
    // Limpa o token e o tempo de expiração (logout)
    clearAuth() {
      this.token = null;
      this.expiresAt = null;
    },
    // Verifica se o token está expirado
    isTokenExpired() {
      if (!this.expiresAt) return true;
      return new Date() > new Date(this.expiresAt);
    },
  },
  persist: true, // Opcional: Persistir o estado no localStorage
});