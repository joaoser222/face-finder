<template>
  <v-text-field
    v-bind="$attrs"
    v-model="internalValue"
    :type="showPassword ? 'text' : 'password'"
    @input="onInput"
    @update:modelValue="onUpdateModelValue"
  >
    <template #append-inner>
      <v-btn 
        :icon="showPassword ? 'Eye' : 'EyeOff'" 
        tabindex="-1" 
        variant="text"
        @click="togglePasswordVisibility"
        rounded="circle"
        size="small"
        :style="{fontSize: '16px'}"
      >
      </v-btn>
    </template>
  </v-text-field>
</template>

<script>
import { ref, watch } from 'vue';

export default {
  name: 'VPasswordInput',
  inheritAttrs: false, // Evita que os atributos sejam aplicados ao elemento raiz
  props: {
    modelValue: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'input'], // Declara os eventos que serão emitidos
  setup(props, { emit }) {
    const internalValue = ref(props.modelValue);
    const showPassword = ref(false);

    // Atualiza o valor interno quando a prop `modelValue` muda
    watch(
      () => props.modelValue,
      (newValue) => {
        internalValue.value = newValue;
      }
    );

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value;
    };

    const onInput = (event) => {
      emit('input', event); // Reemite o evento `input`
    };

    const onUpdateModelValue = (value) => {
      emit('update:modelValue', value); // Reemite o evento `update:modelValue`
    };

    return {
      internalValue,
      showPassword,
      togglePasswordVisibility,
      onInput,
      onUpdateModelValue,
    };
  },
};
</script>