
export default {
  '-1': {
    icon: 'PhotoX',
    title: 'Processamento falhou',
    description: `Ocorreu um erro durante o processamento da coleção.`,
    showDelete: true
  },
  '0': {
    icon: 'PhotoPause',
    title: 'Descompactando Coleção',
    description: `Aguarde até finalizar o processo de descompactação`,
    showDelete: false
  },
  '1': {
    icon: 'PhotoScan',
    title: 'Indexando coleção',
    description: `Aguarde até que o processo de indexação de faces seja concluído.`,
    showDelete: false
  },
  '2': {
    icon: 'PhotoCheck',
    title: 'Processamento concluído',
    description: `Processamento da coleção finalizado com sucesso.`,
    showDelete: true
  }
}