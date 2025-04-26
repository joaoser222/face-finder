export default {
  '-1': {
    icon: 'UserX',
    title: 'Pesquisa falhou',
    description: `Ocorreu um erro durante o processamento da pesquisa.`,
    showDelete: true
  },
  '0': {
    icon: 'UserPause',
    title: 'Pesquisa em espera',
    description: `Aguarde até o início do processamento da pesquisa.`,
    showDelete: false
  },
  '1': {
    icon: 'UserScan',
    title: 'Pesquisa em processamento',
    description: `Aguarde até que o processo de pesquisa seja concluído.`,
    showDelete: false
  },
  '2': {
    icon: 'UserCheck',
    title: 'Pesquisa concluída',
    description: `A pesquisa foi concluída com sucesso.`,
    showDelete: true
  }
}