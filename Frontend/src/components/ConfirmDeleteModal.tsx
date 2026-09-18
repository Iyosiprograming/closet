import Modal from "./Modal";

interface ConfirmDeleteModalProps {
  title?: string;
  message?: string;
  confirming: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function ConfirmDeleteModal({
  title = "Delete this item?",
  message = "This cannot be undone.",
  confirming,
  onCancel,
  onConfirm,
}: ConfirmDeleteModalProps) {
  return (
    <Modal title={title} onClose={onCancel}>
      <p className="text-sm text-muted">{message}</p>

      <div className="mt-6 flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={confirming}
          className="rounded-full border border-line bg-soft px-5 py-2.5 text-sm text-ink transition-colors hover:border-white/20 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Cancel
        </button>

        <button
          type="button"
          onClick={onConfirm}
          disabled={confirming}
          className="rounded-full bg-red-300/90 px-5 py-2.5 text-sm font-medium text-[#2a0d0d] transition-colors hover:bg-red-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {confirming ? "Deleting..." : "Delete"}
        </button>
      </div>
    </Modal>
  );
}
