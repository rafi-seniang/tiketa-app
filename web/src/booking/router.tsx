import { type AnchorHTMLAttributes, type MouseEvent, useMemo, useSyncExternalStore } from "react";

/** The site's screens, at real addresses under the base path, so a link can be shared and Back works. */
export type Route =
  | { name: "home" }
  | { name: "film"; id: number }
  | { name: "seats"; id: number }
  | { name: "tickets" };

const BASE = import.meta.env.BASE_URL; // "/" locally, "/tiketa/" on rafilab.com

export function hrefOf(route: Route): string {
  if (route.name === "film") return `${BASE}film/${route.id}`;
  if (route.name === "seats") return `${BASE}showtime/${route.id}`;
  if (route.name === "tickets") return `${BASE}tickets`;
  return BASE;
}

function parse(pathname: string): Route {
  const rest = pathname.startsWith(BASE) ? pathname.slice(BASE.length) : pathname.slice(1);
  const [screen, id] = rest.split("/");
  const number = Number(id);
  if (screen === "film" && number > 0) return { name: "film", id: number };
  if (screen === "showtime" && number > 0) return { name: "seats", id: number };
  if (screen === "tickets") return { name: "tickets" };
  return { name: "home" };
}

function subscribe(onChange: () => void) {
  window.addEventListener("popstate", onChange);
  return () => window.removeEventListener("popstate", onChange);
}

export function useRoute(): Route {
  const pathname = useSyncExternalStore(subscribe, () => window.location.pathname);
  return useMemo(() => parse(pathname), [pathname]);
}

export function navigate(route: Route) {
  window.history.pushState(null, "", hrefOf(route));
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo?.({ top: 0 });
}

/** A real link: it opens in a new tab with a modifier key, and moves inside the site without a reload otherwise. */
export function Link({ to, ...anchor }: { to: Route } & AnchorHTMLAttributes<HTMLAnchorElement>) {
  const follow = (event: MouseEvent<HTMLAnchorElement>) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
    event.preventDefault();
    navigate(to);
  };
  return <a {...anchor} href={hrefOf(to)} onClick={follow} />;
}
