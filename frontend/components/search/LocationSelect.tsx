"use client";
// components/search/LocationSelect.tsx — Task 8.6
// Searchable dropdown populated from /api/locations (real dataset values).

import { useState, useEffect, useRef } from "react";
import { fetchLocations } from "@/lib/api";
import styles from "./LocationSelect.module.css";

interface Props {
  value:    string;
  onChange: (v: string) => void;
}

export default function LocationSelect({ value, onChange }: Props) {
  const [locations, setLocations] = useState<string[]>([]);
  const [query,     setQuery]     = useState(value);
  const [open,      setOpen]      = useState(false);
  const [loading,   setLoading]   = useState(true);
  const wrapRef = useRef<HTMLDivElement>(null);

  // Fetch locations from the API once on mount
  useEffect(() => {
    fetchLocations().then(locs => {
      setLocations(locs);
      setLoading(false);
    });
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Filter by what the user typed
  const filtered = query.trim().length < 1
    ? locations
    : locations.filter(l => l.toLowerCase().includes(query.toLowerCase()));

  function select(loc: string) {
    setQuery(loc);
    onChange(loc.toLowerCase());
    setOpen(false);
  }

  return (
    <div className={styles.wrapper} ref={wrapRef}>
      <label className={styles.label} htmlFor="location-input">Location</label>

      <div className={`${styles.inputRow} ${open ? styles.focused : ""}`}>
        <span className="material-symbols-outlined" style={{ fontSize: 20, color: "var(--on-surface-v)", flexShrink: 0 }}>
          location_on
        </span>
        <input
          id="location-input"
          type="text"
          autoComplete="off"
          placeholder={loading ? "Loading locations…" : "Search area, e.g. Banashankari"}
          value={query}
          disabled={loading}
          className={styles.input}
          onChange={e => { setQuery(e.target.value); onChange(""); setOpen(true); }}
          onFocus={() => setOpen(true)}
          aria-label="Select location"
          aria-expanded={open}
          aria-haspopup="listbox"
        />
        {query && (
          <button
            className={styles.clear}
            onClick={() => { setQuery(""); onChange(""); setOpen(true); }}
            aria-label="Clear location"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>
          </button>
        )}
        <span className="material-symbols-outlined" style={{ fontSize: 20, color: "var(--on-surface-v)", flexShrink: 0 }}>
          {open ? "expand_less" : "expand_more"}
        </span>
      </div>

      {open && (
        <div className={styles.dropdown} role="listbox" aria-label="Locations">
          {filtered.length === 0 ? (
            <div className={styles.noResults}>No matching locations</div>
          ) : (
            filtered.slice(0, 80).map(loc => (
              <button
                key={loc}
                role="option"
                aria-selected={loc.toLowerCase() === value}
                className={`${styles.option} ${loc.toLowerCase() === value ? styles.selected : ""}`}
                onMouseDown={e => { e.preventDefault(); select(loc); }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: "var(--on-surface-v)" }}>
                  location_on
                </span>
                {loc}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
