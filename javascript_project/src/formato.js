export function formatearMiles(valor) {
  let digitos = '';
  for (const c of String(valor)) {
    if (c >= '0' && c <= '9') digitos += c;
  }

  let resultado = '';
  let contador = 0;
  for (let i = digitos.length - 1; i >= 0; i--) {
    resultado = digitos[i] + resultado;
    contador++;
    if (contador % 3 === 0 && i > 0) resultado = '.' + resultado;
  }

  return resultado;
}