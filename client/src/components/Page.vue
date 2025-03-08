<template>
  <div class="d-flex flex-column align-start justify-center w-100 h-100 py-3">
    <div class="mb-3">
      <h1>{{ meta.plural }}</h1>
    </div>
    <v-card class="w-100 pa-3 flex-grow-1">
      <v-card-text>
        <!-- Exibe a lista de itens se não houver um ID na rota -->
        <div v-if="!$route.params.id">
          <div class="d-flex justify-space-between align-center mt-4" v-if="items.length > 0">
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
              @click="viewItem(item)"
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
        </div>

        <!-- Exibe o item selecionado se houver um ID na rota -->
        <div v-else>
          <h2>{{ selectedItem ? selectedItem[displayField] : 'Carregando...' }}</h2>
          <v-divider class="my-4"></v-divider>
          <slot name="item" :item="selectedItem"></slot>
        </div>

        <!-- Dialog para criar -->
        <v-dialog v-model="dialog" max-width="500px">
          <v-card>
            <v-card-title>
              Criar {{ meta.singular }}
            </v-card-title>
      
            <v-card-text>
              <!-- Slot para o formulário personalizado -->
              <slot name="form" 
                :item="newItem"
                :setForm="setForm"
              >
                <!-- Conteúdo padrão caso o slot não seja fornecido -->
                <p>Formulário personalizado não fornecido.</p>
              </slot>
            </v-card-text>
      
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey-darken-1" @click="closeDialog">
                Cancelar
              </v-btn>
              <v-btn 
                color="primary" 
                @click="save" 
                :loading="loading"
                :disabled="!isFormValid"
              >
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

<script>
import api from '@/plugins/axios'

export default {
  props: {
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
    }
  },
  data() {
    return {
      isFormValid: false,
      items: [],
      search: '',
      dialog: false,
      dialogDelete: false,
      loading: false,
      newItem: {}, // Usado apenas para criar novos itens
      selectedItem: null, // Item selecionado para visualização
      formErrors: {}
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(item => 
        item[this.displayField].toLowerCase().includes(this.search.toLowerCase())
      )
    }
  },
  watch: {
    // Observa mudanças no parâmetro `id` da rota
    '$route.params.id': {
      immediate: true,
      handler(id) {
        if (id) {
          this.fetchSelectedItem(id)
        } else {
          this.selectedItem = null
        }
      }
    }
  },
  methods: {
    setForm(data,status) {
      this.isFormValid = status;
      this.newItem = {...data};
    },
    async fetchItems() {
      try {
        this.loading = true
        const data = await api.get(`${this.endpoint}/list`)
        this.items = data
      } catch (error) {
        console.error('Error fetching items:', error)
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    async fetchSelectedItem(id) {
      try {
        this.loading = true
        const data = await api.get(`${this.endpoint}/show/${id}`)
        this.selectedItem = data
      } catch (error) {
        console.error('Error fetching selected item:', error)
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    async save() {
      try {
        this.loading = true
        this.formErrors = {}
        
        const data = await api.post(`${this.endpoint}/create`, this.newItem)
        this.items.push(data)
        this.$emit('saved', data)
        this.closeDialog()
      } catch (error) {
        console.error('Error saving item:', error)
        if (error.response?.data?.errors) {
          this.formErrors = error.response.data.errors
        }
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    async deleteItemConfirm() {
      try {
        this.loading = true
        await api.delete(`${this.endpoint}/delete/${this.selectedItem.id}`)
        const index = this.items.findIndex(item => item.id === this.selectedItem.id)
        this.items.splice(index, 1)
        this.$emit('deleted', this.selectedItem)
        this.closeDelete()
        this.$router.push({ name: this.$route.name }) // Volta para a lista após a exclusão
      } catch (error) {
        console.error('Error deleting item:', error)
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    openDialog() {
      this.newItem = {} // Reseta o novo item
      this.formErrors = {}
      this.dialog = true
    },
    closeDialog() {
      this.dialog = false
      this.newItem = {}
      this.formErrors = {}
    },
    confirmDelete(item) {
      this.selectedItem = item
      this.dialogDelete = true
    },
    closeDelete() {
      this.dialogDelete = false
    },
    handleSearch() {
      this.$emit('search', this.search)
    },
    viewItem(item) {
      this.$router.push({ params: { id: item.id } }) // Navega para a rota com o ID do item
    }
  },
  mounted() {
    this.fetchItems()
    // Carrega o item selecionado se houver um ID na rota ao montar o componente
    if (this.$route.params.id) {
      this.fetchSelectedItem(this.$route.params.id)
    }
  }
}
</script>