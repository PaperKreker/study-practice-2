import { fireEvent, render, screen } from '@testing-library/react';
import DocumentList from './DocumentList';

test('renders existing documents and refresh action', () => {
  const onRefresh = jest.fn();

  render(
    <DocumentList
      documents={[
        {
          document_id: 'doc-1',
          file_name: 'lecture.pdf',
          size_bytes: 1536,
          uploaded_at: '2024-01-02T03:04:00',
        },
      ]}
      loading={false}
      error={null}
      onRefresh={onRefresh}
    />
  );

  expect(screen.getByText('lecture.pdf')).toBeInTheDocument();
  expect(screen.getByRole('columnheader', { name: 'Размер' })).toBeInTheDocument();
  expect(screen.getByText(/1\.5/)).toBeInTheDocument();

  fireEvent.click(screen.getByRole('button'));

  expect(onRefresh).toHaveBeenCalledTimes(1);
});

test('renders errors and disables refresh while loading', () => {
  const { rerender } = render(
    <DocumentList
      documents={[]}
      loading={false}
      error="Network down"
      onRefresh={jest.fn()}
    />
  );

  expect(screen.getByText('Network down')).toBeInTheDocument();

  rerender(
    <DocumentList
      documents={[]}
      loading
      error={null}
      onRefresh={jest.fn()}
    />
  );

  expect(screen.getByRole('button')).toBeDisabled();
});

test('allows deleting only the current users document', () => {
  const onDelete = jest.fn();
  const ownDocument = {
    id: 'own-document',
    user_id: 'user-1',
    file_name: 'own.pdf',
    size_bytes: 100,
  };

  render(
    <DocumentList
      documents={[
        ownDocument,
        {
          id: 'another-document',
          user_id: 'user-2',
          file_name: 'another.pdf',
          size_bytes: 200,
        },
      ]}
      loading={false}
      error={null}
      onRefresh={jest.fn()}
      currentUserId="user-1"
      onDelete={onDelete}
      deletingId={null}
    />
  );

  expect(screen.queryByRole('button', { name: 'Удалить another.pdf' })).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Удалить own.pdf' }));
  expect(onDelete).toHaveBeenCalledWith(ownDocument);
});

test('disables delete action while document is being deleted', () => {
  render(
    <DocumentList
      documents={[
        {
          id: 'own-document',
          user_id: 'user-1',
          file_name: 'own.pdf',
          size_bytes: 100,
        },
      ]}
      loading={false}
      error={null}
      onRefresh={jest.fn()}
      currentUserId="user-1"
      onDelete={jest.fn()}
      deletingId="own-document"
    />
  );

  expect(screen.getByRole('button', { name: 'Удалить own.pdf' })).toBeDisabled();
});
