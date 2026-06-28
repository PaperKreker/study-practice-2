import { fetchCurrentUser, loginRequest, registerRequest } from './auth';

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

test('loginRequest and registerRequest post credentials', async () => {
  global.fetch
    .mockResolvedValueOnce({ ok: true, json: async () => ({ access_token: 'one' }) })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ access_token: 'two' }) });

  await expect(loginRequest('student', 'secret1')).resolves.toEqual({
    access_token: 'one',
  });
  expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/v1/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'student', password: 'secret1' }),
  });

  await expect(registerRequest('new-user', 'secret2')).resolves.toEqual({
    access_token: 'two',
  });
  expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/v1/users/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'new-user', password: 'secret2' }),
  });
});

test('authentication requests expose backend errors', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status: 401,
    json: async () => ({ detail: 'Invalid credentials' }),
  });

  await expect(loginRequest('student', 'wrong')).rejects.toThrow(
    'Invalid credentials'
  );
});

test('fetchCurrentUser sends bearer token', async () => {
  const user = { id: 'user-1', username: 'student' };
  global.fetch.mockResolvedValueOnce({ ok: true, json: async () => user });

  await expect(fetchCurrentUser('token')).resolves.toEqual(user);
  expect(global.fetch).toHaveBeenCalledWith('/api/v1/users/me', {
    headers: { Authorization: 'Bearer token' },
  });
});
