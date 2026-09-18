import { Menu, X } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

interface NavbarProps {
  onLogout: () => void;
}

const LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/closet", label: "Closet" },
  { to: "/settings", label: "Settings" },
];

function linkClass({ isActive }: { isActive: boolean }): string {
  return [
    "rounded-lg px-3 py-2 text-sm transition-colors",
    isActive ? "bg-soft text-ink" : "text-muted hover:text-ink",
  ].join(" ");
}

export default function Navbar({ onLogout }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
        <NavLink
          to="/dashboard"
          className="font-heading text-sm font-semibold tracking-[0.28em] text-ink"
        >
          CLOSET AI
        </NavLink>

        {/* Desktop */}
        <div className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} className={linkClass}>
              {link.label}
            </NavLink>
          ))}

          <button
            type="button"
            onClick={onLogout}
            className="rounded-lg px-3 py-2 text-sm text-muted transition-colors hover:text-ink"
          >
            Logout
          </button>
        </div>

        {/* Mobile */}
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          className="rounded-lg p-2 text-muted transition-colors hover:text-ink md:hidden"
        >
          {menuOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </nav>

      {menuOpen && (
        <div className="border-t border-line px-5 pb-4 md:hidden">
          <div className="flex flex-col py-2">
            {LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setMenuOpen(false)}
                className={linkClass}
              >
                {link.label}
              </NavLink>
            ))}

            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg px-3 py-2 text-left text-sm text-muted transition-colors hover:text-ink"
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
