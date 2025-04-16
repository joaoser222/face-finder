<template>
  <div>
    <v-dialog
      v-for="(dialog, index) in dialogs"
      :key="index"
      v-model="dialog.isOpen"
      width="500px"
      @after-leave="removeDialog(index)"
      persistent
    >
      <v-card class="pa-3">
        <div class="pa-2">
          <v-card-text class="d-flex flex-column justify-center align-center text-center px-0 pt-0">
            <v-icon :color="dialogTypes[dialog.type].iconColor" size="150px" style="stroke-width: 1.0px" >
              {{ dialogTypes[dialog.type].icon }}
            </v-icon>
            <div class="font-weight-medium pb-4" :style="{'font-size': '28px'}">{{dialog.title}}</div>
            <component :is="dialog.customContent" v-if="dialog.customContent"></component>
            <div class="text-subtitle-1" v-html="dialog.message" v-else></div>
          </v-card-text>
          <v-card-actions>
            <v-row dense class="d-flex flex-row justify-center align-center">
              <v-col cols="12" sm="6" v-if="dialog.showCancelButton" class="d-flex flex-column justify-center align-center">
                <v-btn 
                  color="grey"
                  variant="flat"
                  width="100%"
                  height="40px"
                  max-width="400px"
                  class="text-subtitle-2"
                  text="Cancelar"
                  @click="cancel(index)" 
                  v-bind="dialog.cancelButton"
                >
                </v-btn>
              </v-col>
              <v-col cols="12" sm="6" class="d-flex flex-column justify-center align-center">
                <v-btn 
                  color="primary"
                  variant="flat"
                  width="100%"
                  height="40px"
                  max-width="400px"
                  class="text-subtitle-2"
                  @click="confirm(index)" 
                  text="OK"
                  v-bind="dialog.confirmButton"
                >
                </v-btn>
              </v-col>
            </v-row>
          </v-card-actions>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { reactive } from 'vue';
export default {
  name: 'DialogArea',
  setup() {
    const dialogs = reactive([]);

    const dialogTypes = {
      info: {
        icon: 'InfoCircle',
        iconColor: 'primary'
      },
      question: {
        icon: 'HelpCircle',
        iconColor: 'primary'
      },
      error: {
        icon: 'CircleX',
        iconColor: 'error'
      },
      success: {
        icon: 'CircleCheck',
        iconColor: 'success'
      },
      warning: {
        icon: 'ExclamationCircle',
        iconColor: 'warning'
      }
    }

    const showDialog = (dialog) => {
      dialogs.push({ ...dialog, isOpen: true });
    };

    const close = (index) => {
      let dialog = dialogs[index];
      dialog.isOpen = false;
      if(dialog.onClose) dialog.onClose();
    };

    const confirm = (index) => {
      let dialog = dialogs[index];
      if (dialog.onConfirm) dialog.onConfirm();
      close(index);
    };

    const cancel = (index) => {
      let dialog = dialogs[index];
      if (dialog.onCancel) dialog.onCancel();
      close(index);
    };

    const removeDialog = (index) => {
      dialogs.splice(index,1);
    };

    return { dialogs, showDialog,removeDialog, close, confirm, cancel, dialogTypes };
  },
  expose: ['showDialog'], // Permitir que o método seja acessado externamente
};
</script>
