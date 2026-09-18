import { useEffect, useState } from "react";

import ClothingCard from "../components/ClothingCard";
import ClothingFormModal from "../components/ClothingFormModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import { showToast } from "../components/Toast";
import { ApiError, deleteClothe, getClothes } from "../services/api";
import { CLOTHE_TYPES, type Clothe, type ClotheType } from "../types/api";
import { CLOTHE_TYPE_GROUPS } from "../utils/labels";

type Filter = ClotheType | "all";

export default function Closet() {
  const [clothes, setClothes] = useState<Clothe[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");

  const [addOpen, setAddOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const result = await getClothes();
        if (!cancelled) setClothes(result);
      } catch (caught) {
        if (cancelled) return;
        setLoadError(
          caught instanceof ApiError
            ? caught.message
            : "We couldn't load your closet right now.",
        );
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const editingClothe =
    clothes?.find((clothe) => clothe.id === editingId) ?? null;

  const visible =
    filter === "all"
      ? (clothes ?? [])
      : (clothes ?? []).filter((clothe) => clothe.clothe_type === filter);

  async function handleDelete() {
    if (editingId === null || deleting) return;

    setDeleting(true);

    try {
      await deleteClothe(editingId);

      setClothes((previous) =>
        (previous ?? []).filter((clothe) => clothe.id !== editingId),
      );

      setConfirmOpen(false);
      setEditingId(null);
      showToast("Clothing deleted");
    } catch (caught) {
      showToast(
        caught instanceof ApiError
          ? caught.message
          : "We couldn't delete this item.",
        "error",
      );
    } finally {
      setDeleting(false);
    }
  }

  const filters: Array<{ value: Filter; label: string }> = [
    { value: "all", label: "All" },
    ...CLOTHE_TYPES.map((type) => ({
      value: type as Filter,
      label: CLOTHE_TYPE_GROUPS[type],
    })),
  ];

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink sm:text-3xl">
            My Closet
          </h1>
          <p className="mt-2 text-sm text-muted">
            {clothes ? `${clothes.length} items` : "Loading your closet..."}
          </p>
        </div>

        <button
          type="button"
          onClick={() => setAddOpen(true)}
          className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90"
        >
          + Add outfit
        </button>
      </div>

      <div className="no-scrollbar mt-8 -mx-5 flex gap-2 overflow-x-auto px-5 sm:mx-0 sm:flex-wrap sm:px-0">
        {filters.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => setFilter(option.value)}
            className={[
              "shrink-0 rounded-full border px-4 py-2 text-sm transition-colors",
              filter === option.value
                ? "border-accent bg-accent text-accent-ink"
                : "border-line bg-soft text-muted hover:border-white/20 hover:text-ink",
            ].join(" ")}
          >
            {option.label}
          </button>
        ))}
      </div>

      {loadError && <p className="mt-8 text-sm text-red-300">{loadError}</p>}

      {!clothes && !loadError && (
        <p className="mt-8 text-sm text-muted">Loading your closet...</p>
      )}

      {clothes && clothes.length === 0 && (
        <div className="mt-8 rounded-2xl border border-line bg-card p-6 sm:p-7">
          <p className="text-base font-medium text-ink">
            Your closet is empty
          </p>
          <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted">
            Add your first clothing item.
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

      {clothes && clothes.length > 0 && visible.length === 0 && (
        <p className="mt-8 text-sm text-muted">
          Nothing in this category yet.
        </p>
      )}

      {visible.length > 0 && (
        <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {visible.map((clothe) => (
            <ClothingCard
              key={clothe.id}
              clothe={clothe}
              onClick={() => setEditingId(clothe.id)}
            />
          ))}
        </div>
      )}

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

      {editingClothe && (
        <ClothingFormModal
          mode="edit"
          clothe={editingClothe}
          onClose={() => setEditingId(null)}
          onRequestDelete={() => setConfirmOpen(true)}
          onSaved={(saved) => {
            setClothes((previous) =>
              (previous ?? []).map((clothe) =>
                clothe.id === saved.id ? saved : clothe,
              ),
            );
            setEditingId(null);
            showToast("Clothing updated");
          }}
        />
      )}

      {confirmOpen && (
        <ConfirmDeleteModal
          confirming={deleting}
          onCancel={() => setConfirmOpen(false)}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
}
