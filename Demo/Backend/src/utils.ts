import { spawn } from 'child_process';
import fs from 'fs/promises';

export async function writeFileAsync(
  filePath: string,
  content: string,
): Promise<void> {
  try {
    await fs.writeFile(filePath, content, 'utf-8');
    console.log(`File "${filePath}" has been successfully written.`);
  } catch (error) {
    console.error(`Error writing to file "${filePath}": ${error.message}`);
  }
}

/**
 * Normalize url stripping `..` and `.`
 * @param url
 */
export function normalizeUrl(url: string): string {
  const parts = url.split('/');
  const stack = [];

  for (const part of parts) {
    if (part === '..') {
      stack.pop(); // Go back in directory
    } else if (part !== '.' && part !== '') {
      stack.push(part); // Add part of path
    }
  }

  return stack.join('/');
}

/**
 * Execute command with spawn, print output in console
 * @param command
 * @param args
 */
export function spawnAsync(
  command: string,
  args: string[] = [],
): Promise<string> {
  return new Promise((resolve, reject) => {
    console.log(`Executing command: ${command} ${args.join(' ')}`);
    const child = spawn(command, args);

    let output = '';
    let errorOutput = '';

    child.stdout.on('data', (data) => {
      output += data.toString();
      console.log(data.toString());
    });

    child.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error(data.toString());
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Process exited with code ${code}: ${errorOutput}`));
      }
    });

    child.on('error', (err) => {
      reject(err);
    });
  });
}
