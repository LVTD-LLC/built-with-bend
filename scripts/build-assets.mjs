import { mkdir, copyFile } from 'node:fs/promises';
await mkdir('frontend/static/directory', { recursive: true });
await copyFile('frontend/src/styles/site.css', 'frontend/static/directory/site.css');
await copyFile('frontend/src/js/site.js', 'frontend/static/directory/site.js');
await copyFile('frontend/src/icon.svg', 'frontend/static/directory/icon.svg');
