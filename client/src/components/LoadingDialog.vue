<template>
  <div>
    <v-dialog
      v-model="_dialog"
      max-width="400"
      persistent
    >
      <v-card height="250px" class="d-flex align-center justify-center pa-6">
        <v-progress-circular class="my-6"></v-progress-circular>
        <div class="pt-5 text-subtitle-1 font-weight-light">{{message}}</div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
  import { ref, watch } from 'vue';

  // Recebendo a prop 'propValue' via props
  const props = defineProps({
    dialog: Boolean,  // ou outro tipo, como Number, Object, etc.
    message: String
  });

  // Criando uma variável local baseada no valor da prop
  const _dialog = ref(props.dialog);

  // Watch para observar mudanças na prop e atualizar o valor local
  watch(() => props.dialog, (newValue) => {
    _dialog.value = newValue;
  });

</script>