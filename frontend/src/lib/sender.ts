import { type Writable, writable } from "svelte/store";
import { getElementByXPath, getElementsByXPath, mutationListener } from "./dom";
import { Socket } from "./socket";
import { Delayer } from "./delayer";
import type { Log } from "./log";

type CommandType = "click" | "click_and_type";

export class Sender {
  socket: Socket;
  packets_num: Writable<number>;
  packets_sent: Writable<number>;
  delayer: Delayer;
  log: Log;

  constructor({ send_delay, log }: { send_delay: number; log: Log }) {
    this.socket = new Socket(this.parseCommand);
    this.packets_num = writable(0);
    this.packets_sent = writable(0);
    this.delayer = new Delayer(send_delay * 1000);
    this.log = log;
  }

  async parseCommand(command: any) {
    throw new Error("Not implemented.");
  }

  sendCommand(type: CommandType, data: any) {
    return this.socket.send({ type, data });
  }

  click(element: string | HTMLElement) {
    return this.sendCommand("click", element);
  }

  clickAndType(element: string | HTMLElement, value: string) {
    return this.sendCommand("click_and_type", { element, value });
  }

  async sendMessages(messages: { phone: string; message: string }[]) {
    this.packets_num.set(messages.length);
    for (const { phone, message } of messages) {
      await this.sendMessage(phone, message);
      this.packets_sent.update((x) => x + 1);
    }
  }

  async sendMessage(phone: string, message: string) {
    console.log(`Sending to ${phone}`);
    await this.delayer.wait();
    await this.click('//*[@aria-label="New chat"]');
    await this.clickAndType('//*[@aria-label="Search name or number"]', phone);
    const listitems = await mutationListener(() => {
      const items = getElementsByXPath('//*[@role="listitem"]');
      if (items.length <= 2) return items;
    });
    if (listitems.length != 2) {
      await this.click('//*[@aria-label="Back"]');
      this.log.log(`${phone} non ha Whatsapp.`);
      return false;
    }
    await this.click(listitems[1]);
    await this.clickAndType('//*[@aria-placeholder="Type a message"]', message);
    await this.click('//*[@aria-label="Send"]');
    this.delayer.reset();
    return true;
  }
}
