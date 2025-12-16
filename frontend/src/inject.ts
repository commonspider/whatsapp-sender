import { inject, insertBefore, replaceElement } from "./lib/dom";
import SidebarWidget from "./components/SidebarWidget.svelte";
import { log } from "./lib/log";

const widget_id = "whatsapp-sender-sidebar-widget";

function create_widget_anchor() {
  const anchor = document.createElement("div");
  anchor.setAttribute("id", widget_id);
  return anchor;
}

function replace_sidebar_widget(element: HTMLElement) {
  const anchor = create_widget_anchor();
  replaceElement(element, anchor);
  return anchor;
}

function inject_sidebar_widget(element: HTMLElement) {
  const anchor = create_widget_anchor();
  insertBefore(element, anchor);
  return anchor;
}

inject(SidebarWidget, {
  replace_sidebar_widget: {
    xpath: `//div[@id="${widget_id}"]`,
    injector: replace_sidebar_widget,
  },
  inject_sidebar_widget: {
    xpath: '//*[@aria-label="chat-list-filters"]',
    injector: inject_sidebar_widget,
  },
}).then((_) => log("SidebarWidget injected"));
