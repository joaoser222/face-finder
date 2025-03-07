<template>
  <Page 
    :meta="meta"
    endpoint="/collections"
    display-field="name"
    :form-fields="formFields"
    @saved="handleSaved"
    @deleted="handleDeleted"
    @error="handleError"
  />
</template>

<script setup>
const meta = {
  subtitle: 'Gerencie suas coleções de fotos',
  description: 'Coleções são grupos de fotos que você deve criar para utilizar o algoritmo de pesquisa',
  singular: 'Coleção',
  plural: 'Coleções',
  image: new URL('@/assets/collections.svg', import.meta.url).href
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