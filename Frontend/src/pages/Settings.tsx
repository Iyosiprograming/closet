import { useState } from "react";

import { showToast } from "../components/Toast";
import { ApiError, saveApiKeys, saveLocation } from "../services/api";

interface SettingsProps {
  onLogout: () => void;
}

const sectionClass = "rounded-2xl border border-line bg-card p-6 sm:p-7";
const inputClass =
  "w-full rounded-xl border border-line bg-soft px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-white/25 focus:outline-none";
const labelClass =
  "mb-2 block text-xs uppercase tracking-[0.14em] text-muted";
const primaryButtonClass =
  "rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-60";

export default function Settings({ onLogout }: SettingsProps) {
  const [location, setLocation] = useState("");
  const [locationError, setLocationError] = useState<string | null>(null);
  const [savingLocation, setSavingLocation] = useState(false);

  const [geminiKey, setGeminiKey] = useState("");
  const [openWeatherKey, setOpenWeatherKey] = useState("");
  const [keysError, setKeysError] = useState<string | null>(null);
  const [savingKeys, setSavingKeys] = useState(false);

  async function handleSaveLocation(event: React.FormEvent) {
    event.preventDefault();

    if (savingLocation) return;

    const trimmed = location.trim();

    setLocationError(null);
    setSavingLocation(true);

    try {
      await saveLocation({ location: trimmed });
      showToast(trimmed ? "Location saved" : "Location cleared");
    } catch (caught) {
      setLocationError(
        caught instanceof ApiError
          ? caught.message
          : "We couldn't save your location right now.",
      );
    } finally {
      setSavingLocation(false);
    }
  }

  async function handleSaveKeys(event: React.FormEvent) {
    event.preventDefault();

    if (savingKeys) return;

    const trimmedGemini = geminiKey.trim();

    if (!trimmedGemini) {
      setKeysError("A Gemini API key is required.");
      return;
    }

    setKeysError(null);
    setSavingKeys(true);

    try {
      const trimmedOpenWeather = openWeatherKey.trim();

      await saveApiKeys({
        gemini_api_key: trimmedGemini,
        ...(trimmedOpenWeather
          ? { openweather_api_key: trimmedOpenWeather }
          : {}),
      });

      setGeminiKey("");
      setOpenWeatherKey("");
      showToast("API keys saved");
    } catch (caught) {
      setKeysError(
        caught instanceof ApiError
          ? caught.message
          : "We couldn't save your API keys right now.",
      );
    } finally {
      setSavingKeys(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-5 py-10 sm:px-8 sm:py-14">
      <h1 className="text-2xl font-semibold text-ink sm:text-3xl">
        Settings
      </h1>

      <section className={`mt-8 ${sectionClass}`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink">Location</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">
              Add your city for weather-aware outfit suggestions. This is
              optional.
            </p>
          </div>

          <span className="shrink-0 text-xs text-muted">Optional</span>
        </div>

        <form onSubmit={handleSaveLocation} className="mt-5">
          <label htmlFor="location" className={labelClass}>
            City
          </label>

          <input
            id="location"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="Addis Ababa"
            className={inputClass}
          />

          <p className="mt-2 text-xs text-muted">
            Enter your city only, for example: Addis Ababa.
          </p>

          {locationError && (
            <p role="alert" className="mt-3 text-sm text-red-300">
              {locationError}
            </p>
          )}

          <button
            type="submit"
            disabled={savingLocation}
            className={`mt-5 ${primaryButtonClass}`}
          >
            {savingLocation ? "Saving..." : "Save location"}
          </button>
        </form>
      </section>

      <section className={`mt-6 ${sectionClass}`}>
        <h2 className="text-lg font-semibold text-ink">API configuration</h2>

        <p className="mt-2 text-sm leading-relaxed text-muted">
          Stored on the backend only. Keys are never saved in your browser and
          are cleared from this form after you submit them.
        </p>

        <form onSubmit={handleSaveKeys} className="mt-5 space-y-5">
          <div>
            <div className="flex items-baseline justify-between gap-3">
              <label htmlFor="gemini-api-key" className={`${labelClass} mb-0`}>
                Gemini API key
              </label>

              <span className="text-xs text-muted">Required</span>
            </div>

            <input
              id="gemini-api-key"
              type="password"
              value={geminiKey}
              autoComplete="new-password"
              onChange={(event) => setGeminiKey(event.target.value)}
              className={`mt-2 ${inputClass}`}
            />

            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-block text-xs text-accent underline-offset-4 hover:underline"
            >
              Get a Gemini API key →
            </a>
          </div>

          <div>
            <div className="flex items-baseline justify-between gap-3">
              <label
                htmlFor="openweather-api-key"
                className={`${labelClass} mb-0`}
              >
                OpenWeather API key
              </label>

              <span className="text-xs text-muted">Optional</span>
            </div>

            <input
              id="openweather-api-key"
              type="password"
              value={openWeatherKey}
              autoComplete="new-password"
              onChange={(event) => setOpenWeatherKey(event.target.value)}
              className={`mt-2 ${inputClass}`}
            />

            <a
              href="https://home.openweathermap.org/api_keys"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-block text-xs text-accent underline-offset-4 hover:underline"
            >
              Get an OpenWeather API key →
            </a>
          </div>

          {keysError && (
            <p role="alert" className="text-sm text-red-300">
              {keysError}
            </p>
          )}

          <button
            type="submit"
            disabled={savingKeys}
            className={primaryButtonClass}
          >
            {savingKeys ? "Saving..." : "Save API keys"}
          </button>
        </form>
      </section>

      <section className={`mt-6 ${sectionClass}`}>
        <h2 className="text-lg font-semibold text-ink">Account</h2>

        <p className="mt-2 text-sm leading-relaxed text-muted">
          You are signed in on this device. Logging out clears your session
          cookies.
        </p>

        <button
          type="button"
          onClick={onLogout}
          className="mt-5 rounded-full border border-line bg-soft px-5 py-2.5 text-sm text-ink transition-colors hover:border-white/20"
        >
          Log out
        </button>
      </section>
    </div>
  );
}

