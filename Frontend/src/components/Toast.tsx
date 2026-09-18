import { Check, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";

/**
 * Toasts are used for short confirmations ("Clothing added"). A module-level
 * list keeps this tiny — no context, no provider, no dependency.
 */

type ToastTone = "success" | "error";

interface ToastMessage {
  id: number;
  text: string;
  tone: ToastTone;
}

let nextId = 1;
let messages: ToastMessage[] = [];
let listeners: Array<(next: ToastMessage[]) => void> = [];

function publish(): void {
  for (const listener of listeners) listener([...messages]);
}

/** Show a toast. Safe to call from anywhere, including inside the API layer. */
export function showToast(text: string, tone: ToastTone = "success"): void {
  const message: ToastMessage = { id: nextId++, text, tone };

  messages = [...messages, message];
  publish();

  window.setTimeout(() => {
    messages = messages.filter((item) => item.id !== message.id);
    publish();
  }, 4000);
}

export function ToastContainer() {
  const [items, setItems] = useState<ToastMessage[]>(messages);

  useEffect(() => {
    listeners.push(setItems);
    setItems([...messages]);

    return () => {
      listeners = listeners.filter((listener) => listener !== setItems);
    };
  }, []);

  if (items.length === 0) return null;

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 sm:bottom-6 sm:right-6 sm:left-auto sm:items-end"
    >
      {items.map((item) => (
        <div
          key={item.id}
          className="pointer-events-auto flex w-full max-w-sm items-center gap-3 rounded-xl border border-line bg-card px-4 py-3 text-sm shadow-lg shadow-black/40"
        >
          {item.tone === "success" ? (
            <Check size={16} className="shrink-0 text-accent" />
          ) : (
            <TriangleAlert size={16} className="shrink-0 text-red-300" />
          )}
          <span className="text-ink">{item.text}</span>
        </div>
      ))}
    </div>
  );
}
