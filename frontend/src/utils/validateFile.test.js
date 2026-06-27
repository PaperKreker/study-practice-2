import { MAX_FILE_SIZE } from '../config';
import { validateFile } from './validateFile';

function makeFile({ name, type = '', size = 128 }) {
  return { name, type, size };
}

test('accepts PDF and DOCX files by MIME type or extension', () => {
  expect(validateFile(makeFile({ name: 'lecture.pdf', type: 'application/pdf' }))).toBeNull();
  expect(
    validateFile(
      makeFile({
        name: 'lecture.bin',
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      })
    )
  ).toBeNull();
  expect(validateFile(makeFile({ name: 'lecture.DOCX' }))).toBeNull();
});

test('rejects unsupported file formats', () => {
  expect(validateFile(makeFile({ name: 'notes.txt', type: 'text/plain' }))).toMatch(
    /PDF.*DOCX/
  );
});

test('rejects files bigger than 20 MB', () => {
  expect(validateFile(makeFile({ name: 'large.pdf', size: MAX_FILE_SIZE + 1 }))).toMatch(
    /20/
  );
});
