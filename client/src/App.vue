<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
    <dialog-area ref="dialogArea"/>
    <loading-dialog :dialog="loadingDialogStatus" :message="loadingDialogMessage"></loading-dialog>
  </v-app>
</template>

<script>
import { ref, provide} from 'vue';
import DialogArea from '@/components/DialogArea.vue';
import LoadingDialog from '@/components/LoadingDialog.vue';
export default {
  components:{DialogArea,LoadingDialog},
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
    provide('dialog', dialogCall);
    provide('loadingDialog', loadingDialog);
    return { dialogArea, loadingDialogStatus, loadingDialogMessage };
  }
}
</script>
