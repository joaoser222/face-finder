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
import { VSonner, toast } from 'vuetify-sonner';
export default {
  components:{DialogArea,LoadingDialog,VSonner},
  setup() {
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
        dialogCall({title: "Erro!", type: 'error',message: error.response.data.detail});
      }else{
        dialogCall({title: "Erro!", type: 'error',message: error});
      }
    })
    provide('loadingDialog', loadingDialog);
    return { dialogArea, loadingDialogStatus, loadingDialogMessage };
  }
}
</script>
