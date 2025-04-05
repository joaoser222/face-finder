
export default {
  required: (value) => !!value || "Este campo é obrigatório",
  email: (value) =>(!value || /.+@.+\..+/.test(value)) || "Este campo deve ser um email válido",
  minLength: (length) => (value) => value.length >= length || `Este campo deve ter pelo menos ${length} caracteres`,
  maxLength: (length) => (value) => value.length <= length || `Este campo deve ter no máximo ${length} caracteres`,
  sameAs: (value,reference) => value === reference || "Os valores não coincidem"
}