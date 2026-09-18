import { Shirt } from "lucide-react";
import { useState } from "react";

import { resolveImageUrl } from "../services/api";
import type { Clothe } from "../types/api";
import { CLOTHE_TYPE_NAMES } from "../utils/labels";

interface ClothingCardProps {
  clothe: Clothe;
  onClick?: () => void;
}

export default function ClothingCard({ clothe, onClick }: ClothingCardProps) {
  const [imageFailed, setImageFailed] = useState(false);

  const interactive = Boolean(onClick);

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!interactive}
      className={[
        "group w-full overflow-hidden rounded-2xl border border-line bg-card text-left",
        interactive
          ? "cursor-pointer transition-colors hover:border-white/20"
          : "cursor-default",
      ].join(" ")}
    >
      <div className="aspect-square w-full overflow-hidden bg-soft">
        {imageFailed ? (
          <div className="flex h-full w-full items-center justify-center text-muted">
            <Shirt size={22} />
          </div>
        ) : (
          <img
            src={resolveImageUrl(clothe.image_url)}
            alt={clothe.name}
            loading="lazy"
            onError={() => setImageFailed(true)}
            className="h-full w-full object-cover"
          />
        )}
      </div>

      <div className="px-3 py-3 sm:px-4">
        <p className="truncate text-sm text-ink">{clothe.name}</p>
        <p className="mt-0.5 truncate text-xs text-muted">
          {CLOTHE_TYPE_NAMES[clothe.clothe_type]}
        </p>
      </div>
    </button>
  );
}
