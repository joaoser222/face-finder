<template>
  <v-layout class="mw-100 mh-100">
    <!-- Barra lateral escura -->
    <v-navigation-drawer
      permanent
      color="transparent"
      width="100"
      class="d-flex flex-column align-center pa-2 position-fixed"
      border="0"
      v-if="$vuetify.display.smAndUp"
    >
      <Toolbar />
    </v-navigation-drawer>
    <v-app-bar
      color="transparent"
      height="80"
      class="d-flex flex-column align-center pa-2 position-fixed"
      v-else
    >
      <Toolbar />
    </v-app-bar>

    <!-- Conteúdo principal -->
    <v-main class="bg-grey-lighten-4">
      <v-container fluid class="pt-8 px-6 h-100 w-100">
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script>
import Toolbar from '@/pages/reusables/Toolbar.vue'
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import { ref, inject} from 'vue';
export default {
  components: { Toolbar },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const toast = inject('toast');

    if(!authStore.isAuthenticated()) router.push('/login');
    // Função para criar conexão SSE
    function connectToSSE() {
      const token = authStore.token;

      // Conectar ao endpoint de eventos, passando o token de autenticação
      const eventSource = new EventSource(`/api/sse/events/${token}`);

      const reloadRoute = (name)=>{
        const currentRoute = window.location.pathname.split('/')[1];
        if(name==currentRoute) window.location.reload();
      }
     
      // Tratamento de eventos genéricos
      eventSource.onmessage = function(event) {
        let event_data = JSON.parse(event.data);
        
        toast(event_data.message,{
          duration: 3000,
          cardProps: {
            color: 'success',
          },
          prependIcon: 'Check',
          progressBar: true,
          onDismiss: t => reloadRoute(event_data.entity),
          onAutoClose: t => reloadRoute(event_data.entity),
        });
      };
      
      // Tratamento de erros
      eventSource.onerror = function(error) {
        toast(`Falha ao tentar conectar ao receptor de eventos`,{
          duration: 3000,
          cardProps: {
            color: 'error',
          },
          prependIcon: 'X',
          progressBar: true
        });
          
        // Tentar reconectar após curto intervalo
        setTimeout(() => {
            connectToSSE(token);
        }, 5000);
      };
      
      return eventSource;
    }

    // Chamar ao inicializar o componente
    if(!window.sseConnection) window.sseConnection = connectToSSE();

    return { };
  }
}
</script>

<style scoped>
.v-navigation-drawer :deep(.v-list-item) {
  min-height: 44px;
  padding: 8px;
  justify-content: center;
}

.v-navigation-drawer :deep(.v-list) {
  background-color: transparent;
}
</style>