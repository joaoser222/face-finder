<template>
  <div>
    <v-form>
      <v-row dense>
        <v-col 
          v-for="field in fields" 
          :key="field.name"
          class="px-2 py-1 ma-0" 
          v-bind="field.colProps || {'cols': '12'}"
        >
          <slot :name="`field.${field.name}`" :data="field" :updateForm="updateForm">
            <div class="pb-1 pl-1 text-subtitle-2">{{ field.label }}</div>
            <component
              :is="getComponentType(field.component)"
              v-model="form[field.name]"
              v-bind="field.fieldProps"
              :density="density"
              :error-messages="errorMessages[field.name] || []"
              @input="validate"
            >
              <template v-if="field.type === 'radio'">
                <v-radio 
                  v-for="item in field.items" 
                  :key="item.value"
                  :label="item.label" 
                  :value="item.value"
                />
              </template>
            </component>
          </slot>
        </v-col>
      </v-row>
    </v-form>
  </div>
</template>

<script setup>
import { ref, watch, getCurrentInstance } from 'vue'
import { VTextField, VAutocomplete, VCheckbox, VRadioGroup, VSwitch,VTextarea } from 'vuetify/components'
import VPasswordInput from '@/components/VPasswordInput.vue';
import {Validator} from '@/plugins/validator';
import _ from 'underscore';

const props = defineProps({
  params: {
    type: Object,
    default: () => ({})
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  items: {
    type: Array,
    required: true,
    default: () => ([])
  },
  submitButtonLabel: {
    type: String,
    default: 'Enviar'
  },
  density: {
    type: String,
    default: 'comfortable'
  },
  validateOn: {
    type: String,
    default: 'input'
  }
})

const emit = defineEmits(['update'])

const instance = getCurrentInstance()
const validator = new Validator();
const fields = ref([])
const form = ref({})
const status = ref(false)
const errorMessages = ref({})

const getComponentType = (type = null) => {
  const components = {
    select: VAutocomplete,
    checkbox: VCheckbox,
    radio: VRadioGroup,
    password: VPasswordInput,
    switch: VSwitch,
    textarea: VTextarea,
  }
  return components[type] || VTextField
}

const validate = () => {
  validator.data = form.value
  const { errors, status: currentStatus } = validator.validate()
  status.value = currentStatus
  errorMessages.value = errors
}

const onChange = () => {
  validate()
  emit('update', { 
    form: {...form.value}, 
    status: status.value 
  })
}

const generateForm = () => {
  const data = [...props.items].reduce((agg, item) => {

    // Preenche dados padrão do form
    agg.form[item.name] = item.default ?? (item.type === 'select' ? [] : null)

    const fixedFieldProps = ['name', 'label', 'colProps', 'component']
    const field = {
      ..._.pick(item, fixedFieldProps),
      fieldProps: _.omit(item, [...fixedFieldProps, 'validation'])
    }

    // Adiciona validação se existir
    if (item.validation) {
      if (item.validation.includes('required')) {
        field.label = `*${field.label}`
      }
      agg.schema[item.name] = item.validation
    }

    agg.fields.push(field)
    return agg
  }, {
    form: {},
    schema: {},
    fields: [],
  })

  fields.value = data.fields
  updateForm(data.form)
  validator.schema = data.schema
}

const updateForm = (data) => {
  if (Object.values(data).some(v => v !== null)) {
    form.value = { ...form.value, ...data }
  }
}

// Watchers
watch(() => props.items, (newVal, oldVal) => {
  if (!_.isEqual(newVal, oldVal)) {
    generateForm()
  }
}, { immediate: true })

watch(form, onChange, { deep: true })

watch(() => props.params, (newVal, oldVal) => {
  if (!_.isEqual(newVal, form.value) && Object.keys(newVal).length > 0) {
    updateForm(newVal)
  }
}, { immediate: true })

watch(() => props.errors, (newVal) => {
  errorMessages.value = { ...errorMessages.value, ...newVal }
})
</script>

