import { Sender } from "./lib/sender";

export const sender = new Sender({
  send_delay: 10,
});
export const socket = sender.socket;

window["WhatsappSender"] = { socket, sender };
