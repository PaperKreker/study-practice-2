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
