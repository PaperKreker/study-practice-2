import { render, screen } from '@testing-library/react';
import Highlight from './Highlight';

test('highlights every query term with a mark element', () => {
  render(<Highlight text="Elastic search basics" query="elastic basics" />);

  expect(screen.getByText('Elastic').tagName).toBe('MARK');
  expect(screen.getByText('basics').tagName).toBe('MARK');
});

test('escapes special regexp characters in the query', () => {
  render(<Highlight text="Use c++ syntax" query="c++" />);

  expect(screen.getByText('c++').tagName).toBe('MARK');
});

test('renders original text when query is empty', () => {
  render(<Highlight text="No highlighting" query="" />);

  expect(screen.getByText('No highlighting')).toBeInTheDocument();
});
