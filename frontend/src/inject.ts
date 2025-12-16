import { inject, insertBefore, replaceElement } from "./lib/dom";
import SidebarWidget from "./components/SidebarWidget.svelte";
import Main from "./components/Main.svelte";
import { log } from "./lib/log";

// MAIN

inject(Main, '//h1[contains(text(),"WhatsApp Web")]', (element) => {
  const anchor = document.createElement("div");
  const container = element.parentElement?.parentElement?.parentElement;
  if (container === undefined || container === null)
    throw new Error("Could not inject main");
  else return replaceElement(container, anchor);
}).then(() => log("Main injected"));

// SIDEBAR WIDGET

inject(SidebarWidget, '//*[@aria-label="chat-list-filters"]', (element) => {
  const anchor = document.createElement("div");
  return insertBefore(element, anchor);
}).then((_) => log("SidebarWidget injected"));
