import { useState } from "react";

/** Frontend-only choices; whatever is selected is sent as the `occasion` value. */
const OCCASIONS = [
  "Home",
  "Office",
  "Gym",
  "Date",
  "Party",
  "Casual",
  "Travel",
] as const;

const OTHER = "Other";

interface OccasionSelectorProps {
  /**
   * Reports the value that should be sent as `occasion` to
   * GET /clothes/ai-suggestion, or null when nothing usable is picked yet.
   */
  onOccasionChange: (occasion: string | null) => void;
  disabled?: boolean;
}

export default function OccasionSelector({
  onOccasionChange,
  disabled = false,
}: OccasionSelectorProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [customText, setCustomText] = useState("");

  function choose(preset: string) {
    setSelected(preset);
    onOccasionChange(preset.toLowerCase());
  }

  function chooseOther() {
    setSelected(OTHER);
    const text = customText.trim();
    onOccasionChange(text || null);
  }

  function updateCustomText(text: string) {
    setCustomText(text);
    onOccasionChange(text.trim() || null);
  }

  return (
    <div>
      <div className="no-scrollbar -mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
        {[...OCCASIONS, OTHER].map((preset) => {
          const isActive = selected === preset;

          return (
            <button
              key={preset}
              type="button"
              disabled={disabled}
              onClick={() => (preset === OTHER ? chooseOther() : choose(preset))}
              className={[
                "shrink-0 rounded-full border px-4 py-2 text-sm transition-colors",
                isActive
                  ? "border-accent bg-accent text-accent-ink"
                  : "border-line bg-soft text-muted hover:border-white/20 hover:text-ink",
                disabled ? "cursor-not-allowed opacity-60" : "",
              ].join(" ")}
            >
              {preset}
            </button>
          );
        })}
      </div>

      {selected === OTHER && (
        <div className="mt-4">
          <label
            htmlFor="custom-occasion"
            className="mb-2 block text-xs uppercase tracking-[0.14em] text-muted"
          >
            Describe your occasion
          </label>

          <textarea
            id="custom-occasion"
            rows={3}
            value={customText}
            disabled={disabled}
            onChange={(event) => updateCustomText(event.target.value)}
            placeholder="Dinner with friends at a nice restaurant..."
            className="w-full resize-none rounded-xl border border-line bg-soft px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-white/25 focus:outline-none"
          />
        </div>
      )}
    </div>
  );
}
