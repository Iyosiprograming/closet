import { Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import ClothingCard from "../components/ClothingCard";
import ClothingFormModal from "../components/ClothingFormModal";
import OccasionSelector from "../components/OccasionSelector";
import { showToast } from "../components/Toast";
import { ApiError, getAiSuggestion, getClothes } from "../services/api";
import type { Clothe } from "../types/api";

/** How many cards the dashboard previews before sending you to the closet. */
const PREVIEW_COUNT = 4;

const cardClass = "rounded-2xl border border-line bg-card p-6 sm:p-7";

/** Three up on desktop, two up on very small screens. */
const resultGridClass =
  "grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-3";

export default function Dashboard() {
  const [clothes, setClothes] = useState<Clothe[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [addOpen, setAddOpen] = useState(false);

  const [occasion, setOccasion] = useState<string | null>(null);
  const [outfit, setOutfit] = useState<Clothe[] | null>(null);
  const [outfitError, setOutfitError] = useState<string | null>(null);
  const [suggesting, setSuggesting] = useState(false);

  const loadClothes = useCallback(async () => {
    setLoadError(null);

    try {
      setClothes(await getClothes());
    } catch (caught) {
      setLoadError(
        caught instanceof ApiError
          ? caught.message
          : "We couldn't load your closet right now.",
      );
    }
  }, []);

  useEffect(() => {
    void loadClothes();
  }, [loadClothes]);

  async function handleSuggest() {
    if (!occasion || suggesting) return;

    setSuggesting(true);
    setOutfitError(null);

    try {
      setOutfit(await getAiSuggestion(occasion));
    } catch {
      // Raw backend errors stay out of the UI.
      setOutfit(null);
      setOutfitError(
        "We couldn't create an outfit right now. Please check your API configuration and try again.",
      );
    } finally {
      setSuggesting(false);
    }
  }

  const preview = (clothes ?? []).slice(0, PREVIEW_COUNT);
  const hasClothes = (clothes?.length ?? 0) > 0;

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
      <section>
        <p className="text-xs uppercase tracking-[0.2em] text-muted">
          Your wardrobe
        </p>
        <h1 className="mt-3 max-w-xl text-3xl font-semibold leading-tight text-ink sm:text-4xl">
          What are you wearing today?
        </h1>
        <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted sm:text-base">
          Choose an occasion and let Closet AI build an outfit from the clothes
          you already own.
        </p>
      </section>

      <section className="mt-12">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-ink">Your closet</h2>

          <button
            type="button"
            onClick={() => setAddOpen(true)}
            className="shrink-0 rounded-full border border-line bg-soft px-4 py-2 text-sm text-ink transition-colors hover:border-white/20"
          >
            + Add outfit
          </button>
        </div>

        {loadError && <p className="mt-6 text-sm text-red-300">{loadError}</p>}

        {!clothes && !loadError && (
          <p className="mt-6 text-sm text-muted">Loading your closet...</p>
        )}

        {clothes && !hasClothes && (
          <div className={`mt-6 ${cardClass}`}>
            <p className="text-base font-medium text-ink">
              Your closet is empty
            </p>
            <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted">
              Add your first item to start getting personalized outfit
              suggestions.
            </p>
            <button
              type="button"
              onClick={() => setAddOpen(true)}
              className="mt-5 rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90"
            >
              + Add your first item
            </button>
          </div>
        )}

        {hasClothes && (
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {preview.map((clothe) => (
              <ClothingCard key={clothe.id} clothe={clothe} />
            ))}
          </div>
        )}
      </section>

      <section className={`mt-12 ${cardClass}`}>
        <div className="flex items-center gap-2 text-muted">
          <Sparkles size={14} />
          <span className="font-heading text-xs font-semibold tracking-[0.24em]">
            CLOSET AI
          </span>
        </div>

        <h2 className="mt-4 text-xl font-semibold text-ink">
          Get an outfit suggestion
        </h2>
        <p className="mt-2 max-w-lg text-sm leading-relaxed text-muted">
          Tell Closet AI where you're going and we'll create an outfit using
          your wardrobe.
        </p>

        <div className="mt-6">
          <OccasionSelector
            onOccasionChange={(next) => {
              setOccasion(next);
              setOutfit(null);
              setOutfitError(null);
            }}
            disabled={suggesting}
          />
        </div>

        <button
          type="button"
          onClick={handleSuggest}
          disabled={!occasion || suggesting || !hasClothes}
          className="mt-6 w-full rounded-full bg-accent px-5 py-3 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:px-8"
        >
          {suggesting ? "Creating your outfit..." : "Get suggestion"}
        </button>

        {!hasClothes && clothes && (
          <p className="mt-3 text-xs text-muted">
            Add a few items before asking for an outfit.
          </p>
        )}

        <div className="mt-10 border-t border-line pt-8">
          {suggesting && (
            <p className="text-sm text-muted">Creating your outfit...</p>
          )}

          {!suggesting && outfitError && (
            <p role="alert" className="max-w-md text-sm text-red-300">
              {outfitError}
            </p>
          )}

          {!suggesting && !outfitError && outfit && outfit.length > 0 && (
            <>
              <h3 className="text-lg font-semibold text-ink">Your outfit</h3>
              <div className={`mt-5 ${resultGridClass}`}>
                {outfit.map((clothe) => (
                  <ClothingCard key={clothe.id} clothe={clothe} />
                ))}
              </div>
            </>
          )}

          {!suggesting && !outfitError && (!outfit || outfit.length === 0) && (
            <p className="max-w-sm text-sm leading-relaxed text-muted">
              No outfit suggestion yet. Choose an occasion to get started.
            </p>
          )}
        </div>
      </section>

      {addOpen && (
        <ClothingFormModal
          mode="create"
          onClose={() => setAddOpen(false)}
          onSaved={(saved) => {
            setClothes((previous) => [...(previous ?? []), saved]);
            setAddOpen(false);
            showToast("Clothing added");
          }}
        />
      )}
    </div>
  );
}
