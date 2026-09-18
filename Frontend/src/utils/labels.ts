import type {
  ClotheType,
  Formality,
  Season,
} from "../types/api";

/**
 * Friendly labels for the backend enum values. Only the *labels* differ from
 * the API — requests always send the raw enum values in `types/api.ts`.
 */

/** Singular, used on a clothing card ("Top", "Bottoms" would read oddly there). */
export const CLOTHE_TYPE_NAMES: Record<ClotheType, string> = {
  top: "Top",
  bottom: "Bottom",
  shoes: "Shoes",
  underwear: "Underwear",
  hat: "Hat",
  outerwear: "Outerwear",
  accessory: "Accessory",
  other: "Other",
};

/** Plural, used for filter chips and section titles. */
export const CLOTHE_TYPE_GROUPS: Record<ClotheType, string> = {
  top: "Tops",
  bottom: "Bottoms",
  shoes: "Shoes",
  underwear: "Underwear",
  hat: "Hats",
  outerwear: "Outerwear",
  accessory: "Accessories",
  other: "Other",
};

export const SEASON_NAMES: Record<Season, string> = {
  sunny: "Sunny",
  rainy: "Rainy",
  all: "All seasons",
};

export const FORMALITY_NAMES: Record<Formality, string> = {
  casual: "Casual",
  formal: "Formal",
  homewear: "Homewear",
};

/** "A lightly worn cotton shirt" -> "Top · All seasons · Casual" */
export function describeClothe(
  clotheType: ClotheType,
  season: Season,
  formality: Formality,
): string {
  return [
    CLOTHE_TYPE_NAMES[clotheType],
    SEASON_NAMES[season],
    FORMALITY_NAMES[formality],
  ].join(" · ");
}
