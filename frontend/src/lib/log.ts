import type { Writable } from "svelte/store";
import { writable } from "svelte/store";

export class Log {
  lines: Writable<string[]>;

  constructor() {
    this.lines = writable([]);
  }

  log(message: string) {
    this.lines.update((lines) => {
      lines.push(message);
      return lines;
    });
  }
}
