import { fireEvent, render, screen } from '@testing-library/react';
import Pagination from './Pagination';

test('does not render when there is only one page', () => {
  const { container } = render(
    <Pagination page={1} totalPages={1} onPageChange={jest.fn()} />
  );

  expect(container).toBeEmptyDOMElement();
});

test('renders compact page controls and calls onPageChange', () => {
  const onPageChange = jest.fn();

  render(<Pagination page={5} totalPages={10} onPageChange={onPageChange} />);

  expect(screen.getByRole('button', { name: '5' })).toHaveAttribute(
    'aria-current',
    'page'
  );

  fireEvent.click(screen.getByRole('button', { name: '6' }));

  expect(onPageChange).toHaveBeenCalledWith(6);
});

test('disables boundary navigation buttons', () => {
  const { rerender } = render(
    <Pagination page={1} totalPages={3} onPageChange={jest.fn()} />
  );

  expect(screen.getAllByRole('button')[0]).toBeDisabled();

  rerender(<Pagination page={3} totalPages={3} onPageChange={jest.fn()} />);

  expect(screen.getAllByRole('button').at(-1)).toBeDisabled();
});
