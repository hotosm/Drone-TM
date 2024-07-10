/* eslint-disable import/prefer-default-export */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Removes specified keys from an object.
 *
 * @param {Object} obj - The original object to remove keys from.
 * @param {Array<string>} keysToRemove - An array of key names to be removed from the object.
 * @returns {Object} A new object with the specified keys removed.
 *
 * @example
 * const originalObj = { a: 1, b: 2, c: 3, d: 4 };
 * const keysToRemove = ['b', 'd'];
 * const result = removeKeys(originalObj, keysToRemove);
 * // result is { a: 1, c: 3 }
 */
export function removeKeysFromObject(
  obj: Record<string, any>,
  keysToRemove: any[],
) {
  return Object.fromEntries(
    Object.entries(obj).filter(([key]) => !keysToRemove.includes(key)),
  );
}
