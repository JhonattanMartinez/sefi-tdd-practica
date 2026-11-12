// formato.js - HU-01: separador de miles para los campos de dinero (COP).

/** Deja solo los dígitos: '1.500.000' -> '1500000'. */
export function soloDigitos(valor) {
  return String(valor).replace(/\D/g, '');
}

/** 1500000 -> '1.500.000'. Inserta un punto antes de cada grupo de 3 dígitos. */
export function formatearMiles(valor) {
  return soloDigitos(valor).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}