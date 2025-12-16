import {error} from "./log";

let command_index_counter = 0;

interface Command {
  id: number;
  type: string;
  data: any;
}

class Socket {
  commands: Command[];
  resolves: Map<number, (boolean) => void>;

  constructor() {
    this.commands = [];
    this.resolves = new Map();
  }

  runCommand(type: string, data: any) {
    return new Promise((resolve) => {
      const id = command_index_counter;
      command_index_counter++;
      this.resolves.set(id, resolve);
      this.commands.push({ id, type, data });
    });
  }

  getCommand(callback: (Command) => void) {
    const command = this.commands.shift();
    callback(command);
  }

  sendResult(id: number, data: boolean) {
    const resolve = this.resolves.get(id);
    if (resolve == undefined) {
      error("No resolve found for command id: " + id);
    } else {
      this.resolves.delete(id);
      resolve(data);
    }
  }
}

export const socket = new Socket();

window["WhatsappSenderSocket"] = socket;
