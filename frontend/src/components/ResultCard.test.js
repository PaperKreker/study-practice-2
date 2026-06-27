import { render, screen } from '@testing-library/react';
import ResultCard from './ResultCard';

test('renders search result metadata and rounded score', () => {
  const result = {
    file_name: 'lecture.pdf',
    page: 3,
    text: 'Elastic search fragment',
    score: 1.234,
  };

  const { container } = render(<ResultCard result={result} query="search" />);

  expect(screen.getByText('lecture.pdf')).toBeInTheDocument();
  expect(screen.getByText('1.23')).toBeInTheDocument();
  expect(container.querySelector('.result-card__meta')).toHaveTextContent('3');
  expect(screen.getByText('search').tagName).toBe('MARK');
});

test('renders fallbacks for missing title and score', () => {
  const { container } = render(
    <ResultCard result={{ text: 'fragment' }} query="" />
  );

  expect(container.querySelector('.result-card__file')).not.toBeEmptyDOMElement();
  expect(container.querySelector('.result-card__score')).not.toBeEmptyDOMElement();
});
