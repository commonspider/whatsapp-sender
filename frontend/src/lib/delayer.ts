import { sleep } from "./utils";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";

export class Delayer {
  delay: number;
  sleep_until: number;
  countdown: Writable<number | undefined>;
  countdown_delay: number;

  constructor(delay: number, countdown_delay: number = 1000) {
    this.delay = delay;
    this.sleep_until = 0;
    this.countdown = writable();
    this.countdown_delay = countdown_delay;
  }

  async wait() {
    while (true) {
      const total_delay = this.sleep_until - Date.now();
      if (total_delay <= 0) break;
      this.countdown.set(total_delay);
      await sleep(Math.min(this.countdown_delay, total_delay));
    }
    this.countdown.set(undefined);
  }

  reset() {
    this.sleep_until = Date.now() + this.delay;
  }
}
