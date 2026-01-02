import { Sender } from "./lib/sender";
import { getElementByXPath, getElementsByXPath } from "./lib/dom";
import { Log } from "./lib/log";

export const log = new Log();
export const sender = new Sender({
  send_delay: 20,
  log,
});
export const socket = sender.socket;

window["WhatsappSender"] = {
  socket,
  sender,
  dom: { getElementByXPath, getElementsByXPath },
  log,
};
