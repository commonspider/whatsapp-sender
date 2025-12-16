export function format(value: string, dictionary: { [key: string]: string }) {
  return value.replace(/{(.+)}/g, (match, number) =>
    dictionary[number] !== undefined ? dictionary[number] : match,
  );
}

export function range(n: number) {
  return [...Array(n).keys()];
}

export function zipObject(keys: string[], values: string[]) {
  const n = Math.min(keys.length, values.length);
  return Object.fromEntries(range(n).map((i) => [keys[i], values[i]]));
}

export function sleep(seconds: number) {
  return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}
