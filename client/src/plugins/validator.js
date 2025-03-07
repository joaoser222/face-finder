  
class Validator {
  constructor(data={}, schema={}) {
    this.data = data; // Objeto a ser validado
    this.schema = schema; // Esquema de validação
    this.errors = {}; // Mensagens de erro
    this.status = true;
  }

  inputValidation(rule,param=null){
    /**
     * Realiza validação em dados de acordo com a regra de validação
     * 
     * @param {string} rule - Nome da regra para validação
     * @param {string} param - Parametros secundários para a regra de validação
  
      */
    let validators = {
      required: (value) => !!value || "Este campo é obrigatório",
      required_with: (value) => !!value && !!this.data[param] || "Este campo é obrigatório",
      email: (value) =>(!value || /.+@.+\..+/.test(value)) || "Este campo deve ser um email válido",
      min: (value) => {
        let min_val = param;
        return (!value || (value && value.length >= min_val)) || `Este campo deve ter pelo menos ${min_val} caracteres`
      },
      max: (value) => {
        let max_val = param;
        return (!value || (value && value.length <= max_val) )|| `Este campo deve ter no máximo ${max_val} caracteres`
      }
    }
    return validators[rule];
  }

  /**
   * Executa a validação com base no esquema fornecido.
   * @returns {Object} - Mensagens de erro para cada campo.
   */
  validate() {
    this.errors = Object.entries(this.schema).reduce((agg,entry) => {
      let [field, expression] = entry;
      let fieldValue = this.data[field];
      let rules = expression.split("|");

      let errorMessages = rules.reduce((f_agg,rule)=>{
        let [ruleName, param] = rule.split(":");
        let validationRule = this.inputValidation(ruleName,param);

        if (!validationRule) {
          throw new Error(`Regra de validação desconhecida: ${ruleName}`);
        }

        let result = validationRule(fieldValue);
        if (result !== true) f_agg.push(result);
        return f_agg;
      },[])

      if(errorMessages.length>0) agg[field] = errorMessages;

      return agg;
    },{});

    this.status = Object.keys(this.errors).length==0;
    return {errors: this.errors, status: this.status};
  }
}
  
export {Validator};