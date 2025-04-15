
export default {
  required: (value) => !!value || "Este campo é obrigatório",
  email: (value) =>(!value || /.+@.+\..+/.test(value)) || "Este campo deve ser um email válido",
  minLength: (length, reference_name='caractere(s)') => (value) => value.length >= length || `Este campo deve ter pelo menos ${length} ${reference_name}`,
  maxLength: (length, reference_name='caractere(s)') => (value) => value.length <= length || `Este campo deve ter no máximo ${length} ${reference_name}`,
  sameAs: (value,reference) => value === reference || "Os valores não coincidem"
}