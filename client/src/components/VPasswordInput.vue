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
      />
    </template>
  </v-text-field>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'input'])

const internalValue = ref(props.modelValue)
const showPassword = ref(false)

watch(() => props.modelValue, (newValue) => {
  internalValue.value = newValue
})

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const onInput = (event) => {
  emit('input', event)
}

const onUpdateModelValue = (value) => {
  emit('update:modelValue', value)
}
</script>