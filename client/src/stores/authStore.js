import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    expires_at: null,
    user: {},
  }),
  actions: {
    setAuth(data) {
      this.token = data.token;
      this.expires_at = data.expires_at;
      this.user = data.user;
    },
    setUser(data){
      this.user = data;
    },
    clearAuth() {
      this.token = null;
      this.expires_at = null;
      this.user = {};
    },
    isAuthenticated() {
      let status = this.token && new Date() < new Date(this.expires_at);
      if(!status) this.clearAuth();
      return status;
    },
  },
  persist: true, // Opcional: Persistir o estado no localStorage
});