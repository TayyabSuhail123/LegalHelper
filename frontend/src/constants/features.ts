export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain', // Added TXT support to match backend
] as const;

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB to match backend
