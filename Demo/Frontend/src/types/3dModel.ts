export type ModelSelectOption = {
  url: string;
  name: string;
}

export function isModelSelectOption(value: unknown): value is ModelSelectOption {
  return (
    typeof value === "object" &&
    value !== null &&
    "url" in value &&
    "name" in value &&
    typeof (value as Record<string, unknown>).url === "string" &&
    typeof (value as Record<string, unknown>).name === "string"
  );
}