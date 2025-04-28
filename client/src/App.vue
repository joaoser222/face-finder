<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
    <dialog-area ref="dialogArea"/>
    <v-sonner :visible-toasts="5" expand position="bottom-right"/>
    <loading-dialog :dialog="loadingDialogStatus" :message="loadingDialogMessage"></loading-dialog>
  </v-app>
</template>

<script>
import { ref, provide} from 'vue';
import DialogArea from '@/components/DialogArea.vue';
import LoadingDialog from '@/components/LoadingDialog.vue';
import { useRouter, useRoute} from 'vue-router';
import { VSonner, toast } from 'vuetify-sonner';

export default {
  components:{DialogArea,LoadingDialog,VSonner},
  setup() {
    const router = useRouter();
    const currentRoute = useRoute();
    const dialogArea = ref(null);
    const loadingDialogStatus = ref(false);
    const loadingDialogMessage = ref('');

    const dialogCall = (options)=>{
      if (dialogArea.value) {
        dialogArea.value.showDialog(options);
      }else{
        setTimeout(() => {
          dialogCall(options);
        }, 100);
      }
    }

    const getAssetUrl = function(path){
      return new URL(path, import.meta.url).href;
    };

    const loadingDialog = {
      show: function(msg){
        loadingDialogStatus.value = true;
        loadingDialogMessage.value = msg || 'Carregando';
      },
      hide: function () {
        loadingDialogStatus.value = false;
        loadingDialogMessage.value = '';
      }
    }

    provide('toast', toast);
    provide('dialog', dialogCall);
    provide('catchRequestErrors',(error)=>{
      if (error.response?.data?.detail) {
        if([403,401].includes(error.response.status)) return router.push('/login');
        dialogCall({title: "Erro!", type: 'error',message: error.response.data.detail});
      }else{
        dialogCall({title: "Erro!", type: 'error',message: error});
      }
    })
    provide('loadingDialog', loadingDialog);
    provide('getAssetUrl', getAssetUrl);
    provide('currentRouteParams', ()=>{
      return currentRoute.params
    });

    provide('formatBytes',function (bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';

      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

      // Determina a unidade com base no valor máximo
      const maxSizeIndex = Math.floor(Math.log(bytes) / Math.log(k));
      const i = Math.min(maxSizeIndex, sizes.length - 1);

      return parseFloat((bytes / Math.pow(k, i))).toFixed(dm) + ' ' + sizes[i];
    });

    return { dialogArea, loadingDialogStatus, loadingDialogMessage };
  }
}
</script>
