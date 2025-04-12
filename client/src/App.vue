<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
    <dialog-area ref="dialogArea"/>
  </v-app>
</template>

<script>
import { ref, provide} from 'vue';
import DialogArea from '@/components/DialogArea.vue';
export default {
  components:{DialogArea},
  setup() {
    const dialogArea = ref(null);
    const dialogCall = (options)=>{
      if (dialogArea.value) {
        dialogArea.value.showDialog(options);
      }else{
        setTimeout(() => {
          dialogCall(options);
        }, 100);
      }
    }
    provide('dialog', dialogCall);
    return { dialogArea };
  }
}
</script>
