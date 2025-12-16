import { writable } from "svelte/store";
import {sleep} from "./utils";
import {socket} from "./socket";
import {getElementsByXPath, mutationListener, waitForElement, waitForElements} from "./dom";

export const n_packets = writable(0);
export const packets_sent = writable(0);

export async function sendPackets(
  packets: { phone: string; message: string }[],
) {
  n_packets.set(packets.length);
  for (const { phone, message } of packets) {
    const result = await sendPacket(phone, message);
    if (result) packets_sent.update((x) => x + 1);
    else n_packets.update((x) => x - 1);
    await sleep(10);
  }
}

async function sendPacket(phone: string, message: string) {
  await socket.execute("click", '//*[@aria-label="New chat"]');
  await socket.execute("click_and_type", {
    element: '//*[@aria-label="Search name or number"]',
    value: phone,
  });
  const listitems = await mutationListener(() => {
    const items = getElementsByXPath('//*[@role="listitem"]');
    if (items.length <= 2) return items;
  })
  if (listitems.length != 2) return false;

  await socket.execute("click", listitems[1]);
  await socket.execute("click_and_type", {
    element: '//*[@aria-placeholder="Type a message"]',
    value: message,
  });
  await socket.execute("click", '//*[@aria-label="Send"]');
  return true;
}
