export function format(value: string, dictionary: { [key: string]: string }) {
  return value.replace(/{(.+)}/g, (match, number) =>
    dictionary[number] !== undefined ? dictionary[number] : match,
  );
}

export function range(n: number) {
  return [...Array(n).keys()];
}

export function zipObject<T>(keys: string[], values: T[]) {
  const n = Math.min(keys.length, values.length);
  return Object.fromEntries(range(n).map((i) => [keys[i], values[i]]));
}

function timestamp() {
  return Date.now() / 1000;
}

export function sleep(seconds: number) {
  if (sleep > 0)
    return new Promise((resolve) => setTimeout(resolve, seconds * 1000));
  else return Promise.resolve();
}

export class Delayer {
  delay: number;
  sleep_until: number;

  constructor(delay: number) {
    this.delay = delay;
    this.sleep_until = 0;
  }

  async wait() {
    await sleep(this.sleep_until - timestamp());
  }

  done() {
    this.sleep_until = timestamp() + this.delay;
  }
}
