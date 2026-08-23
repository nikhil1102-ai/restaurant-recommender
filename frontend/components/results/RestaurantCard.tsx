"use client";
// components/results/RestaurantCard.tsx — Task 8.16

import Image from "next/image";
import RankBadge from "@/components/ui/RankBadge";
import styles from "./RestaurantCard.module.css";
import type { Restaurant } from "@/types/api";

interface Props {
  restaurant: Restaurant;
  onSave:     (name: string) => void;
  isSaved:    boolean;
  delay?:     number;
}

const FOOD_SEEDS = [1080, 292, 493, 326, 431, 835, 999, 674, 112, 430];

export default function RestaurantCard({ restaurant, onSave, isSaved, delay = 0 }: Props) {
  const { rank, name, cuisine, cost, rating, votes, location, ai_summary } = restaurant;
  const seed     = FOOD_SEEDS[rank % FOOD_SEEDS.length];
  const imageUrl = `https://picsum.photos/seed/food${seed}/400/300`;

  return (
    <article
      className={`anim-fade-up ${styles.card}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Image */}
      <div className={`card-image ${styles.imageWrap}`}>
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="192px"
          className={styles.image}
          priority={rank <= 2}
        />
        <RankBadge rating={rating} />
        {/* Rank number top-right */}
        <div className={styles.rankNum}>#{rank}</div>
      </div>

      {/* Body */}
      <div className={`card-body ${styles.body}`}>
        <div className={styles.header}>
          <h3 className={styles.name}>{name}</h3>
          <button
            className={styles.bookmark}
            onClick={() => onSave(name)}
            aria-label={isSaved ? "Unsave restaurant" : "Save restaurant"}
          >
            <span className={`material-symbols-outlined ${isSaved ? "icon-fill" : ""}`}
              style={{ color: isSaved ? "var(--primary)" : undefined }}>
              bookmark{isSaved ? "" : "_border"}
            </span>
          </button>
        </div>

        <div className={styles.tags}>
          {cuisine.split(",").slice(0, 3).map(c => (
            <span key={c} className={styles.chip}>{c.trim()}</span>
          ))}
          <span className={styles.dot}>•</span>
          <span className={styles.meta}>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>location_on</span>
            {location}
          </span>
          <span className={styles.dot}>•</span>
          <span className={styles.meta}>₹{cost} for two</span>
          <span className={styles.dot}>•</span>
          <span className={styles.meta}>{votes.toLocaleString()} votes</span>
        </div>

        <blockquote className={styles.quote}>"{ai_summary}"</blockquote>
      </div>
    </article>
  );
}
