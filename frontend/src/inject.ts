import { inject, insertBefore, replaceElement } from "./lib/dom";
import SidebarWidget from "./components/SidebarWidget.svelte";
import Main from "./components/Main.svelte";

// Main

inject(Main, '//h1[contains(text(),"WhatsApp Web")]', (anchor) => {
  const element = document.createElement("div");
  const container = anchor.parentElement?.parentElement?.parentElement;
  if (container === undefined || container === null)
    throw new Error("Could not inject main");
  else return replaceElement(container, element);
}).then(() => console.log("Main injected"));

// Sidebar Widget

inject(SidebarWidget, '//*[@aria-label="chat-list-filters"]', (anchor) => {
  const element = document.createElement("div");
  return insertBefore(anchor, element);
}).then(() => console.log("SidebarWidget injected"));
