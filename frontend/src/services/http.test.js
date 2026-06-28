import { authHeaders, buildUrl, extractErrorMessage } from './http';

test('buildUrl and authHeaders create request metadata', () => {
  expect(buildUrl('/api/v1/search')).toBe('/api/v1/search');
  expect(authHeaders('token')).toEqual({ Authorization: 'Bearer token' });
  expect(authHeaders()).toEqual({});
});

test('extractErrorMessage reads string and validation details', async () => {
  await expect(
    extractErrorMessage({
      status: 400,
      json: async () => ({ detail: 'Bad request' }),
    })
  ).resolves.toBe('Bad request');

  await expect(
    extractErrorMessage({
      status: 422,
      json: async () => ({ detail: [{ msg: 'Invalid username' }, { code: 2 }] }),
    })
  ).resolves.toBe('Invalid username; {"code":2}');
});

test('extractErrorMessage supports message and non-JSON fallbacks', async () => {
  await expect(
    extractErrorMessage({
      status: 409,
      json: async () => ({ message: 'Already exists' }),
    })
  ).resolves.toBe('Already exists');

  await expect(
    extractErrorMessage({
      status: 503,
      json: async () => {
        throw new Error('not json');
      },
    })
  ).resolves.toBe('Ошибка сервера (503)');
});
