/**
 * TypeScript type definitions for PathForm
 */

export type PathFormValue = string | number | boolean | null | PathFormObject | PathFormArray;
export type PathFormObject = { [key: string]: PathFormValue };
export type PathFormArray = PathFormValue[];

export interface PathFormError extends Error {
    name: string;
    message: string;
}

/**
 * Parse PathForm text into a TypeScript object (JSON-compatible).
 */
export function parsePathform(text: string): PathFormObject;

/**
 * Parse a value string into a TypeScript value.
 */
export function parseValue(valueStr: string): PathFormValue;

/**
 * Set a value at a given path in the object.
 */
export function setPath(obj: PathFormObject, pathStr: string, value: PathFormValue): void;

/**
 * Convert PathForm text to JSON string.
 */
export function toJSON(pathformText: string, indent?: number): string;

/**
 * Convert JSON object to PathForm text.
 */
export function fromJSON(jsonObj: PathFormObject | string, flat?: boolean): string;

declare const _default: {
    parse: typeof parsePathform;
    parseValue: typeof parseValue;
    setPath: typeof setPath;
    toJSON: typeof toJSON;
    fromJSON: typeof fromJSON;
};

export default _default;

