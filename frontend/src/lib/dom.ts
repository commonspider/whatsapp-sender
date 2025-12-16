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

export function waitForFirstElement(xpath: { [k: string]: string }) {
  return mutationListener(() => {
    for (const [name, xp] of Object.entries(xpath)) {
      const element = getElementByXPath(xp);
      if (element !== null) return [name, element];
    }
  });
}

export async function inject(
  component:
    | ComponentType<SvelteComponent<{}>>
    | Component<{}, Record<string, any>, any>,
  injectors: {
    [name: string]: { xpath: string; injector: (HTMLElement) => HTMLElement };
  },
) {
  const [selected, element] = await waitForFirstElement(
    Object.fromEntries(
      Object.entries(injectors).map(([n, { xpath }]) => [n, xpath]),
    ),
  );
  const injected = await injectors[selected].injector(element);
  mount(component, { target: injected });
  return injected;
}

export function insertBefore(anchor: HTMLElement, node: HTMLElement) {
  anchor.parentNode?.insertBefore(node, anchor);
}

export function insertAfter(anchor: HTMLElement, node: HTMLElement) {
  anchor.parentNode?.insertBefore(node, anchor.nextSibling);
}

export function replaceElement(element: HTMLElement, other: HTMLElement) {
  element.parentNode?.replaceChild(other, element);
}
