import { formatDate, formatFileSize } from './format';

test('formatFileSize handles empty and byte values', () => {
  expect(formatFileSize()).toBe('');
  expect(formatFileSize(0)).toMatch(/^0 /);
  expect(formatFileSize(512)).toMatch(/^512 /);
});

test('formatFileSize scales larger values', () => {
  expect(formatFileSize(1024)).toContain('1.0');
  expect(formatFileSize(1024 * 1024 * 2.5)).toContain('2.5');
});

test('formatDate handles invalid and valid dates', () => {
  expect(formatDate()).toHaveLength(1);
  expect(formatDate('not-a-date')).toHaveLength(1);
  expect(formatDate('2024-01-02T03:04:00')).toContain('2024');
});
