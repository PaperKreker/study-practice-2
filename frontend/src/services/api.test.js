import { fetchDocuments, searchDocuments } from './api';

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
