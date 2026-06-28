import {
  clearSearchHistory,
  deleteDocument,
  fetchDocuments,
  fetchDocumentStatus,
  fetchSearchHistory,
  searchDocuments,
  uploadDocument,
} from './api';

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

test('searchDocuments calls backend search endpoint with page and size', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [
      {
        chunk_id: 'doc_0',
        file_name: 'lecture.pdf',
        page: 1,
        text: 'Elasticsearch text',
        score: 2.5,
      },
    ],
  });

  const result = await searchDocuments('elastic search', 2, 10);

  expect(global.fetch).toHaveBeenCalledWith(
    '/api/v1/search?q=elastic+search&page=2&size=10'
  );
  expect(result).toEqual({
    results: [
      {
        chunk_id: 'doc_0',
        file_name: 'lecture.pdf',
        page: 1,
        text: 'Elasticsearch text',
        score: 2.5,
      },
    ],
    total: 1,
  });
});

test('fetchDocuments normalizes backend DocumentListResponse with items', async () => {
  const documents = [
    {
      id: 'document-id',
      file_name: 'lecture.pdf',
      size_bytes: 128,
      chunk_count: 2,
    },
  ];
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ total: 1, items: documents }),
  });

  await expect(fetchDocuments()).resolves.toEqual(documents);
  expect(global.fetch).toHaveBeenCalledWith('/api/v1/documents');
});

test('searchDocuments normalizes backend SearchResponse with items and total', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      total: 42,
      items: [
        {
          chunk_id: 'doc_0',
          file_name: 'lecture.pdf',
          page: 1,
          text: 'Elasticsearch text',
          score: 2.5,
        },
      ],
    }),
  });

  const result = await searchDocuments('elastic search', 2, 10);

  expect(global.fetch).toHaveBeenCalledWith(
    '/api/v1/search?q=elastic+search&page=2&size=10'
  );
  expect(result).toEqual({
    results: [
      {
        chunk_id: 'doc_0',
        file_name: 'lecture.pdf',
        page: 1,
        text: 'Elasticsearch text',
        score: 2.5,
      },
    ],
    total: 42,
  });
});

test('searchDocuments extracts error message from backend detail', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status: 500,
    json: async () => ({ detail: 'Search failed' }),
  });

  await expect(searchDocuments('elastic')).rejects.toThrow('Search failed');
});

test('fetchDocuments sends token and private document filters', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ items: [] }),
  });

  await fetchDocuments('token', { limit: 20, offset: 40, myDocs: true });

  expect(global.fetch).toHaveBeenCalledWith(
    '/api/v1/documents?limit=20&offset=40&my_docs=true',
    { headers: { Authorization: 'Bearer token' } }
  );
});

test('document status and deletion use authenticated endpoints', async () => {
  global.fetch
    .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'doc-1' }) })
    .mockResolvedValueOnce({ ok: true });

  await expect(fetchDocumentStatus('doc-1', 'token')).resolves.toEqual({
    id: 'doc-1',
  });
  await expect(deleteDocument('doc-1', 'token')).resolves.toBeUndefined();

  expect(global.fetch).toHaveBeenNthCalledWith(1, '/api/v1/documents/doc-1', {
    headers: { Authorization: 'Bearer token' },
  });
  expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/v1/documents/doc-1', {
    method: 'DELETE',
    headers: { Authorization: 'Bearer token' },
  });
});

test('searchDocuments sends bearer token when provided', async () => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ items: [], total: 0 }),
  });

  await searchDocuments('private', 1, 10, 'token');

  expect(global.fetch).toHaveBeenCalledWith(
    '/api/v1/search?q=private&page=1&size=10',
    { headers: { Authorization: 'Bearer token' } }
  );
});

test('search history endpoints preserve pagination and authentication', async () => {
  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [{ query: 'elastic' }], total: 1 }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ deleted: 1, message: 'cleared' }),
    });

  await expect(
    fetchSearchHistory('token', { limit: 10, offset: 20 })
  ).resolves.toEqual({ items: [{ query: 'elastic' }], total: 1 });
  await expect(clearSearchHistory('token')).resolves.toEqual({
    deleted: 1,
    message: 'cleared',
  });

  expect(global.fetch).toHaveBeenNthCalledWith(
    1,
    '/api/v1/search/history?limit=10&offset=20',
    { headers: { Authorization: 'Bearer token' } }
  );
  expect(global.fetch).toHaveBeenNthCalledWith(2, '/api/v1/search/history', {
    method: 'DELETE',
    headers: { Authorization: 'Bearer token' },
  });
});

test('uploadDocument sends token and reports upload progress', async () => {
  const originalXhr = global.XMLHttpRequest;
  let xhr;

  class FakeXMLHttpRequest {
    constructor() {
      this.upload = {};
      this.headers = {};
      xhr = this;
    }

    open(method, url) {
      this.method = method;
      this.url = url;
    }

    setRequestHeader(name, value) {
      this.headers[name] = value;
    }

    send(body) {
      this.body = body;
    }
  }

  global.XMLHttpRequest = FakeXMLHttpRequest;
  const onProgress = jest.fn();
  const request = uploadDocument(
    new File(['content'], 'lecture.pdf'),
    onProgress,
    'token'
  );

  xhr.upload.onprogress({ lengthComputable: true, loaded: 5, total: 10 });
  xhr.status = 201;
  xhr.responseText = JSON.stringify({ document_id: 'doc-1' });
  xhr.onload();

  await expect(request).resolves.toEqual({ document_id: 'doc-1' });
  expect(xhr.method).toBe('POST');
  expect(xhr.url).toBe('/api/v1/documents/upload');
  expect(xhr.headers.Authorization).toBe('Bearer token');
  expect(onProgress).toHaveBeenCalledWith(50);
  global.XMLHttpRequest = originalXhr;
});

test('uploadDocument returns backend upload errors', async () => {
  const originalXhr = global.XMLHttpRequest;
  let xhr;

  class FakeXMLHttpRequest {
    constructor() {
      this.upload = {};
      xhr = this;
    }

    open() {}
    setRequestHeader() {}
    send() {}
  }

  global.XMLHttpRequest = FakeXMLHttpRequest;
  const request = uploadDocument(new File(['content'], 'lecture.pdf'));
  xhr.status = 400;
  xhr.responseText = JSON.stringify({ detail: 'Unsupported file' });
  xhr.onload();

  await expect(request).rejects.toThrow('Unsupported file');
  global.XMLHttpRequest = originalXhr;
});
