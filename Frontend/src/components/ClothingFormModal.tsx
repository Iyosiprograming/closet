import { Upload } from "lucide-react";
import { useEffect, useId, useState } from "react";

import { ApiError, createClothe, resolveImageUrl, updateClothe } from "../services/api";
import {
  CLOTHE_TYPES,
  FORMALITIES,
  SEASONS,
  type Clothe,
  type ClotheType,
  type Formality,
  type Season,
} from "../types/api";
import {
  CLOTHE_TYPE_GROUPS,
  FORMALITY_NAMES,
  SEASON_NAMES,
} from "../utils/labels";
import Modal from "./Modal";

interface ClothingFormModalProps {
  mode: "create" | "edit";
  /** Required in edit mode. */
  clothe?: Clothe;
  onClose: () => void;
  onSaved: (clothe: Clothe) => void;
  onRequestDelete?: () => void;
}

const inputClass =
  "w-full rounded-xl border border-line bg-soft px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-white/25 focus:outline-none";
const labelClass =
  "mb-2 block text-xs uppercase tracking-[0.14em] text-muted";

export default function ClothingFormModal({
  mode,
  clothe,
  onClose,
  onSaved,
  onRequestDelete,
}: ClothingFormModalProps) {
  const fieldId = useId();

  const [name, setName] = useState(clothe?.name ?? "");
  const [color, setColor] = useState(clothe?.color ?? "");
  const [clotheType, setClotheType] = useState<ClotheType>(
    clothe?.clothe_type ?? "top",
  );
  const [season, setSeason] = useState<Season>(clothe?.season ?? "all");
  const [formality, setFormality] = useState<Formality>(
    clothe?.formality ?? "casual",
  );
  const [image, setImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Preview the chosen file locally. The object URL is always revoked.
  useEffect(() => {
    if (!image) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(image);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [image]);

  function handleFileChange(file: File | null) {
    if (file && !file.type.startsWith("image/")) {
      setError("Please choose an image file.");
      return;
    }

    setError(null);
    setImage(file);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    if (saving) return;

    const trimmedName = name.trim();
    const trimmedColor = color.trim();

    if (!trimmedName || !trimmedColor) {
      setError("Please add a name and a color.");
      return;
    }

    if (mode === "create" && !image) {
      setError("Please choose an image.");
      return;
    }

    setError(null);
    setSaving(true);

    try {
      const saved =
        mode === "create"
          ? await createClothe({
              image,
              name: trimmedName,
              color: trimmedColor,
              clothe_type: clotheType,
              season,
              formality,
            })
          : await updateClothe(clothe!.id, {
              ...(clothe!.name !== trimmedName ? { name: trimmedName } : {}),
              ...(clothe!.color !== trimmedColor ? { color: trimmedColor } : {}),
              ...(clothe!.clothe_type !== clotheType
                ? { clothe_type: clotheType }
                : {}),
              ...(clothe!.season !== season ? { season } : {}),
              ...(clothe!.formality !== formality ? { formality } : {}),
              ...(image ? { image } : {}),
            });

      onSaved(saved);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setSaving(false);
    }
  }

  const currentImage = previewUrl ?? (clothe ? resolveImageUrl(clothe.image_url) : null);

  return (
    <Modal
      title={mode === "create" ? "Add clothing" : "Edit clothing"}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <span className={labelClass}>Image</span>

          <div className="flex items-center gap-4">
            {currentImage && (
              <img
                src={currentImage}
                alt="Selected clothing"
                className="h-20 w-20 shrink-0 rounded-xl border border-line object-cover"
              />
            )}

            <label
              htmlFor={`${fieldId}-image`}
              className="flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-line bg-soft px-4 py-4 text-sm text-muted transition-colors hover:border-white/20 hover:text-ink"
            >
              <Upload size={16} />
              <span className="truncate">
                {image
                  ? image.name
                  : mode === "edit"
                    ? "Replace image"
                    : "Choose an image"}
              </span>
            </label>

            <input
              id={`${fieldId}-image`}
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={(event) =>
                handleFileChange(event.target.files?.[0] ?? null)
              }
            />
          </div>
        </div>

        <div>
          <label htmlFor={`${fieldId}-name`} className={labelClass}>
            Name
          </label>
          <input
            id={`${fieldId}-name`}
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="White Oxford Shirt"
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor={`${fieldId}-color`} className={labelClass}>
            Color
          </label>
          <input
            id={`${fieldId}-color`}
            value={color}
            onChange={(event) => setColor(event.target.value)}
            placeholder="White"
            className={inputClass}
          />
        </div>

        <div className="grid gap-5 sm:grid-cols-3">
          <div>
            <label htmlFor={`${fieldId}-type`} className={labelClass}>
              Clothing type
            </label>
            <select
              id={`${fieldId}-type`}
              value={clotheType}
              onChange={(event) =>
                setClotheType(event.target.value as ClotheType)
              }
              className={inputClass}
            >
              {CLOTHE_TYPES.map((type) => (
                <option key={type} value={type} className="bg-card">
                  {CLOTHE_TYPE_GROUPS[type]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor={`${fieldId}-season`} className={labelClass}>
              Season
            </label>
            <select
              id={`${fieldId}-season`}
              value={season}
              onChange={(event) => setSeason(event.target.value as Season)}
              className={inputClass}
            >
              {SEASONS.map((value) => (
                <option key={value} value={value} className="bg-card">
                  {SEASON_NAMES[value]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor={`${fieldId}-formality`} className={labelClass}>
              Formality
            </label>
            <select
              id={`${fieldId}-formality`}
              value={formality}
              onChange={(event) =>
                setFormality(event.target.value as Formality)
              }
              className={inputClass}
            >
              {FORMALITIES.map((value) => (
                <option key={value} value={value} className="bg-card">
                  {FORMALITY_NAMES[value]}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-300">
            {error}
          </p>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          {mode === "edit" && onRequestDelete ? (
            <button
              type="button"
              onClick={onRequestDelete}
              disabled={saving}
              className="rounded-full px-3 py-2 text-sm text-muted transition-colors hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Delete item
            </button>
          ) : (
            <span />
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="rounded-full border border-line bg-soft px-5 py-2.5 text-sm text-ink transition-colors hover:border-white/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={saving}
              className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving
                ? mode === "create"
                  ? "Adding clothing..."
                  : "Saving..."
                : mode === "create"
                  ? "Add clothing"
                  : "Save changes"}
            </button>
          </div>
        </div>
      </form>
    </Modal>
  );
}
