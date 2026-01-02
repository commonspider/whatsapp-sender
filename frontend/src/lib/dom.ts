import {
  type Component,
  type ComponentType,
  mount,
  type SvelteComponent,
} from "svelte";

export function getElementByXPath(xpath: string): HTMLElement | null {
  return document.evaluate(
    xpath,
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null,
  ).singleNodeValue as HTMLElement;
}

export function getElementsByXPath(xpath: string) {
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.ORDERED_NODE_ITERATOR_TYPE,
    null,
  );
  const nodes: HTMLElement[] = [];
  let item = result.iterateNext();
  while (item !== null) {
    nodes.push(item as HTMLElement);
    item = result.iterateNext();
  }
  return nodes;
}

export function mutationListener<T>(
  listener: (mutations: MutationRecord[]) => T | undefined,
): Promise<T> {
  return new Promise(async (resolve) => {
    const result = await listener([]);
    if (result !== undefined) return resolve(result);

    const observer = new MutationObserver(
      async (mutations: MutationRecord[]) => {
        const result = await listener(mutations);
        if (result !== undefined) {
          observer.disconnect();
          resolve(result);
        }
      },
    );

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });
}

export function waitForElement(xpath: string) {
  return mutationListener(() => {
    const element = getElementByXPath(xpath);
    if (element !== null) return element;
  });
}

export function waitForElements(xpath: string) {
  return mutationListener(() => {
    const elements = getElementsByXPath(xpath);
    if (elements.length > 0) return elements;
  });
}

export async function inject(
  component:
    | ComponentType<SvelteComponent<{}>>
    | Component<{}, Record<string, any>, any>,
  xpath: string,
  injector: (Element) => Element,
) {
  const element = await waitForElement(xpath);
  const injected = injector(element);
  mount(component, { target: injected });
  return injected;
}

export function insertBefore(anchor: Element, element: Element) {
  anchor.parentElement?.insertBefore(element, anchor);
  return anchor;
}

export function insertAfter(anchor: Element, element: Element) {
  anchor.parentElement?.insertBefore(element, anchor.nextSibling);
  return element;
}

export function replaceElement(anchor: Element, element: Element) {
  anchor.parentElement?.replaceChild(element, anchor);
  return element;
}
