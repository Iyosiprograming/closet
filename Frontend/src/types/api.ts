/**
 * TypeScript mirrors of the FastAPI Pydantic schemas in
 * `Backend/app/Schemas`. Every enum value below must match
 * `Backend/app/Models/clothe_model.py` exactly — the API is the source of truth.
 */

/** ClotheType */
export const CLOTHE_TYPES = [
  "top",
  "bottom",
  "shoes",
  "underwear",
  "hat",
  "outerwear",
  "accessory",
  "other",
] as const;

export type ClotheType = (typeof CLOTHE_TYPES)[number];

/** SeasonType */
export const SEASONS = ["sunny", "rainy", "all"] as const;

export type Season = (typeof SEASONS)[number];

/** FormalityType */
export const FORMALITIES = ["casual", "formal", "homewear"] as const;

export type Formality = (typeof FORMALITIES)[number];

/** ClotheResponseSchema */
export interface Clothe {
  id: number;
  user_id: number;
  image_url: string;
  name: string;
  color: string;
  clothe_type: ClotheType;
  season: Season;
  formality: Formality;
  created_at: string;
}

/** UserCreateSchema — used by POST /users/ (registration). */
export interface UserCreate {
  username: string;
  password: string;
}

/** LoginUserSchema — POST /users/login takes the same shape. */
export type LoginUser = UserCreate;

/** UserCreateResponseSchema */
export interface UserCreateResponse {
  id: number;
  username: string;
}

/** AddApiKey — PATCH /users/api-keys */
export interface AddApiKey {
  gemini_api_key: string;
  openweather_api_key?: string | null;
}

/** AddLocation — PATCH /users/location */
export interface AddLocation {
  location?: string | null;
}

/** MessageResponseSchema */
export interface MessageResponse {
  message: string;
}

/**
 * GET /health — readiness probe. The desktop launcher polls it to know when the
 * backend is up; the UI uses `desktop` to tell whether a desktop launcher is
 * running Closet AI (the only case where it can quit itself).
 */
export interface AppStatus {
  status: string;
  app: string;
  version: string;
  desktop: boolean;
}

/**
 * The multipart fields accepted by POST /clothes/ and PATCH /clothes/{id}.
 * `image` is a real file, so these payloads are always sent as FormData.
 */
export interface ClotheFormValues {
  image?: File | null;
  name: string;
  color: string;
  clothe_type: ClotheType;
  season: Season;
  formality: Formality;
}
