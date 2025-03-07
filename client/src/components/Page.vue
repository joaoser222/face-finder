<template>
  <div class="d-flex flex-column align-start justify-center w-100 h-100 py-3">
    <div class="mb-3">
      <h1>{{ meta.plural }}</h1>
    </div>
    <v-card class="w-100 pa-3 flex-grow-1">
      <v-card-text>
        <div class="d-flex justify-space-between align-center" v-if="items.length > 0">
          <div class="pr-2 w-100">
            <v-text-field 
              v-model="search" 
              label="Pesquisar" 
              color="primary" 
              hide-details 
              single-line 
              density="compact"
              @input="handleSearch"
            />
          </div>
          <div>
            <v-btn color="primary" @click="openDialog()">
              <v-icon>Plus</v-icon>Criar {{ meta.singular }}
            </v-btn>
          </div>
        </div>

        <!-- Lista de itens -->
        <v-list v-if="items.length > 0" class="mt-4">
          <v-list-item
            v-for="item in filteredItems"
            :key="item.id"
            :title="item[displayField]"
          >
            <template v-slot:append>
              <v-btn
                icon="Pencil"
                size="small"
                @click="openDialog(item)"
              />
              <v-btn
                icon="Trash"
                size="small"
                color="error"
                @click="confirmDelete(item)"
              />
            </template>
          </v-list-item>
        </v-list>

        <!-- Estado vazio -->
        <v-empty-state v-else>
          <template v-slot:media>
            <div class="d-flex flex-column justify-center align-center">
              <v-img :src="meta.image" width="350px" height="auto"></v-img>
            </div>
          </template>

          <template v-slot:title>
            <div class="text-h6 mt-8">
              {{ meta.subtitle }}
            </div>
          </template>
  
          <template v-slot:text>
            <div class="text-caption">
              {{ meta.description }}
            </div>
          </template>
  
          <template v-slot:actions>
            <v-btn color="primary" @click="openDialog()">
              <v-icon>Plus</v-icon>Criar {{ meta.singular }}
            </v-btn>
          </template>
        </v-empty-state>

        <!-- Dialog para criar/editar -->
        <v-dialog v-model="dialog" max-width="500px">
          <v-card>
            <v-card-title>
              {{ editedItem.id ? `Editar ${meta.singular}` : `Criar ${meta.singular}` }}
            </v-card-title>

            <v-card-text>
              <DataForm
                ref="formRef"
                :items="formFields"
                :params="editedItem"
                :errors="formErrors"
                @update="handleFormUpdate"
              >
                <template v-for="(_, name) in $slots" :key="name" v-slot:[name]="slotData">
                  <slot :name="name" v-bind="slotData"/>
                </template>
              </DataForm>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey-darken-1" @click="closeDialog">
                Cancelar
              </v-btn>
              <v-btn color="primary" @click="save" :loading="loading">
                Salvar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Dialog de confirmação -->
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title>Tem certeza que deseja excluir este item?</v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey-darken-1" @click="closeDelete">Não</v-btn>
              <v-btn color="error"  @click="deleteItemConfirm" :loading="loading">Sim</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/plugins/axios'
import DataForm from '@/components/DataForm.vue'

const props = defineProps({
  meta: {
    type: Object,
    required: true,
    validator: (prop) => {
      return ['title', 'subtitle', 'description', 'singular', 'plural','image'].every(key => key in prop)
    }
  },
  endpoint: {
    type: String,
    required: true
  },
  displayField: {
    type: String,
    default: 'name'
  },
  formFields: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['error', 'saved', 'deleted', 'search'])

// Refs
const items = ref([])
const search = ref('')
const dialog = ref(false)
const dialogDelete = ref(false)
const loading = ref(false)
const editedItem = ref({})
const formRef = ref(null)
const formErrors = ref({})

// Computed
const filteredItems = computed(() => {
  return items.value.filter(item => 
    item[props.displayField].toLowerCase().includes(search.value.toLowerCase())
  )
})

// Form handling
const handleFormUpdate = ({ form, status }) => {
  editedItem.value = { ...editedItem.value, ...form }
}

// CRUD Operations
const fetchItems = async () => {
  try {
    loading.value = true
    const data = await api.get(props.endpoint)
    items.value = data
  } catch (error) {
    console.error('Error fetching items:', error)
    emit('error', error)
  } finally {
    loading.value = false
  }
}

const save = async () => {
  try {
    loading.value = true
    formErrors.value = {}
    
    if (editedItem.value.id) {
      const data = await api.put(`${props.endpoint}/${editedItem.value.id}`, editedItem.value)
      const index = items.value.findIndex(item => item.id === editedItem.value.id)
      if (index !== -1) items.value[index] = { ...data }
    } else {
      const data = await api.post(props.endpoint, editedItem.value)
      items.value.push(data)
    }
    
    emit('saved', editedItem.value)
    closeDialog()
  } catch (error) {
    console.error('Error saving item:', error)
    if (error.response?.data?.errors) {
      formErrors.value = error.response.data.errors
    }
    emit('error', error)
  } finally {
    loading.value = false
  }
}

const deleteItemConfirm = async () => {
  try {
    loading.value = true
    await api.delete(`${props.endpoint}/${editedItem.value.id}`)
    const index = items.value.findIndex(item => item.id === editedItem.value.id)
    items.value.splice(index, 1)
    emit('deleted', editedItem.value)
    closeDelete()
  } catch (error) {
    console.error('Error deleting item:', error)
    emit('error', error)
  } finally {
    loading.value = false
  }
}

// UI Handlers
const openDialog = (item = {}) => {
  editedItem.value = item.id ? { ...item } : {}
  formErrors.value = {}
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  editedItem.value = {}
  formErrors.value = {}
}

const confirmDelete = (item) => {
  editedItem.value = { ...item }
  dialogDelete.value = true
}

const closeDelete = () => {
  dialogDelete.value = false
  editedItem.value = {}
}

const handleSearch = () => {
  emit('search', search.value)
}

// Fetch items on mount
fetchItems()
</script>