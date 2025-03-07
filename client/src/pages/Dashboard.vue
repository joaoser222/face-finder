<template>
  <div>
    <!-- Cabeçalho -->
    <div class="mb-8">
      <h1 class="text-h3 font-weight-bold mb-6">
        Dashboard
      </h1>

      <!-- Barra de pesquisa -->
      <v-text-field
        prepend-inner-icon="Search"
        placeholder="Procure imagens em coleções"
        variant="outlined"
        hide-details
        class="rounded-lg bg-white"
        style="max-width: 600px"
      ></v-text-field>
    </div>

    <!-- Grid de imagens -->
    <v-row>
      <v-col
        v-for="n in 6"
        :key="n"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          elevation="0"
          class="rounded-lg overflow-hidden"
        >
          <v-img
            :src="`https://picsum.photos/500/300?random=${n}`"
            height="200"
            cover
          ></v-img>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
</script>
