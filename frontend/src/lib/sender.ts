import { type Writable, writable } from "svelte/store";
import { getElementsByXPath, mutationListener } from "./dom";
import { Socket } from "./socket";
import { Delayer } from "./utils";

type CommandType = "click" | "click_and_type";

export class Sender {
  socket: Socket;
  packets_num: Writable<number>;
  packets_sent: Writable<number>;
  delayer: Delayer;

  constructor({ send_delay }: { send_delay: number }) {
    this.socket = new Socket(this.parseCommand);
    this.packets_num = writable(0);
    this.packets_sent = writable(0);
    this.delayer = new Delayer(send_delay);
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
    await this.delayer.wait();
    await this.click('//*[@aria-label="New chat"]');
    await this.clickAndType('//*[@aria-label="Search name or number"]', phone);
    const listitems = await mutationListener(() => {
      const items = getElementsByXPath('//*[@role="listitem"]');
      if (items.length <= 2) return items;
    });
    if (listitems.length != 2) return false;
    await this.click(listitems[1]);
    await this.clickAndType('//*[@aria-placeholder="Type a message"]', message);
    await this.click('//*[@aria-label="Send"]');
    this.delayer.done();
    return true;
  }
}
