<template>
  <Page 
    :meta="meta"
    endpoint="/search"
    display-field="name"
    :form-fields="formFields"
    @saved="handleSaved"
    @deleted="handleDeleted"
    @error="handleError"
  />
</template>

<script setup>
const meta = {
  subtitle: 'Gerencie pesquisas de faces',
  description: 'Pesquisas são consultas em que você utiliza um rosto como referência para encontrar imagens que contenham essa mesma face em diferentes coleções.',
  singular: 'Pesquisa',
  plural: 'Pesquisas',
  image: new URL('@/assets/face_search.svg', import.meta.url).href
}

const formFields = [
  {
    name: 'name',
    label: 'Nome',
    component: 'text',
    validation: 'required',
    colProps: { cols: 12 }
  },
  {
    name: 'description',
    label: 'Descrição',
    component: 'textarea',
    colProps: { cols: 12 }
  }
]

const handleSaved = (item) => {
  console.log('Item saved:', item)
}

const handleDeleted = (item) => {
  console.log('Item deleted:', item)
}

const handleError = (error) => {
  console.error('Error:', error)
}
</script> 