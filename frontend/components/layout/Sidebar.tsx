"use client";
// components/layout/Sidebar.tsx — Task 8.4

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./Sidebar.module.css";

const NAV = [
  { href: "/",        icon: "explore",         label: "Discover"    },
  { href: "/saved",   icon: "bookmark",         label: "Saved"       },
  { href: "/history", icon: "history",          label: "History"     },
  { href: "#",        icon: "settings_suggest", label: "AI Settings" },
];

export default function Sidebar() {
  const path = usePathname();

  return (
    <nav className={`sidebar ${styles.sidebar} scroll`}>
      <div className={styles.links}>
        {NAV.map(({ href, icon, label }) => {
          const active = href !== "#" && path === href;
          return (
            <Link
              key={label}
              href={href}
              className={`${styles.link} ${active ? styles.active : ""}`}
            >
              <span className={`material-symbols-outlined ${active ? "icon-fill" : ""}`}>
                {icon}
              </span>
              <span>{label}</span>
            </Link>
          );
        })}
      </div>

      <div className={styles.concierge}>
        <p className={styles.conciergeLabel}>Concierge Status</p>
        <p className={styles.conciergeBody}>
          AI-curated picks tailored to your taste profile.
        </p>
        <Link href="/" className={styles.newSearch}>
          New Search
        </Link>
      </div>
    </nav>
  );
}
