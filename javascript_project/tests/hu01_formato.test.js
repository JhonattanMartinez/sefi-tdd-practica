import test from 'node:test';
import assert from 'node:assert';
import { formatearMiles } from '../src/formato.js'; // aún no existe -> RED

test('HU-01 CA3: 1500000 se muestra como 1.500.000', () => {
  assert.strictEqual(formatearMiles(1500000), '1.500.000');
});

test('HU-01 CA3: si el usuario sigue escribiendo, el número se reagrupa', () => {
  assert.strictEqual(formatearMiles('1.500.0004'), '15.000.004');
});

test('HU-01 límite: 999 no lleva separador y 1000 sí', () => {
  assert.strictEqual(formatearMiles(999), '999');
  assert.strictEqual(formatearMiles(1000), '1.000');
});

test('HU-01: un campo vacío devuelve cadena vacía', () => {
  assert.strictEqual(formatearMiles(''), '');
});