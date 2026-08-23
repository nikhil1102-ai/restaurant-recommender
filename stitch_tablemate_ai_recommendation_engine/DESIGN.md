---
name: TableMate AI
colors:
  surface: '#131316'
  surface-dim: '#131316'
  surface-bright: '#39393c'
  surface-container-lowest: '#0e0e11'
  surface-container-low: '#1b1b1e'
  surface-container: '#1f1f22'
  surface-container-high: '#2a2a2d'
  surface-container-highest: '#353438'
  on-surface: '#e4e1e6'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e4e1e6'
  inverse-on-surface: '#303033'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#ffb955'
  on-secondary: '#452b00'
  secondary-container: '#dc9100'
  on-secondary-container: '#4f3100'
  tertiary: '#4ae183'
  on-tertiary: '#003919'
  tertiary-container: '#00a657'
  on-tertiary-container: '#003115'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffddb4'
  secondary-fixed-dim: '#ffb955'
  on-secondary-fixed: '#291800'
  on-secondary-fixed-variant: '#633f00'
  tertiary-fixed: '#6bfe9c'
  tertiary-fixed-dim: '#4ae183'
  on-tertiary-fixed: '#00210c'
  on-tertiary-fixed-variant: '#005228'
  background: '#131316'
  on-background: '#e4e1e6'
  surface-variant: '#353438'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

The design system is centered on a **Premium Dark** aesthetic, optimized for high-end restaurant discovery and AI-assisted curation. The brand personality is sophisticated yet approachable, blending a "Concierge" feel with modern technological precision.

The style utilizes **Modern Corporate** foundations mixed with **Glassmorphism** for navigational overlays. Visual interest is generated through high-contrast accents against deep, desaturated surfaces, creating a focused environment that highlights food photography and editorial content.

**Key Visual Principles:**
- **Depth through Layering:** Uses distinct surface tiers rather than aggressive shadows.
- **Precision:** Tight alignment and consistent spacing to reflect AI accuracy.
- **Vibrancy:** Strategic use of coral and gold to signify action and quality.

## Colors

The palette is anchored by a deep charcoal base to reduce eye strain and provide a luxurious backdrop.

- **Primary (#E23744):** A high-energy coral used for critical actions, branding, and active states.
- **Secondary (#F5A623):** An amber gold reserved specifically for ratings, awards, and premium "Top Choice" designations.
- **Success/Tertiary (#2ECC71):** Used for "Table Available" indicators and confirmation states.
- **Surface (#1A1A22):** The standard container color for cards, menus, and input fields.
- **Background (#0F0F12):** The canvas color, providing the deepest level of the UI hierarchy.

## Typography

This design system uses **Inter** exclusively to maintain a clean, systematic feel. The hierarchy relies on substantial weight differences (SemiBold vs Regular) to guide the eye through dense restaurant data.

**Usage Rules:**
- **Display & Headline:** Use for restaurant names and section headers. Apply tight letter-spacing to large sizes for a more "designed" look.
- **Body:** Use for descriptions and reviews. Ensure secondary text colors are used for meta-data (e.g., "300+ reviews") to maintain focus on primary content.
- **Labels:** Use for chips, buttons, and "Rank Badges". All-caps should only be used for `label-sm` in specific UI metadata scenarios.

## Layout & Spacing

The layout utilizes a **12-column fluid grid** for desktop and a **single-column fluid layout** for mobile. 

- **Spacing Rhythm:** Based on a 4px scale. Most components should use `16px` (md) for internal padding.
- **Mobile Safe Areas:** 16px horizontal margins are mandatory.
- **Section Spacing:** Use `32px` (xl) to separate distinct content blocks like "Recommended for You" and "Trending Nearby."
- **Component Density:** Medium. Elements should feel airy enough to present high-quality imagery without feeling sparse.

## Elevation & Depth

Depth is communicated through color and transparency rather than heavy shadows.

- **Level 0 (Background):** #0F0F12. The base canvas.
- **Level 1 (Surface):** #1A1A22. Used for cards and primary content containers.
- **Level 2 (Elevated):** #25252E. Used for modals and hovered states.
- **Glassmorphism:** Headers and navigation bars use a background blur (20px) with #1A1A22 at 70% opacity. A subtle 1px border (#FFFFFF10) should be applied to the bottom or edges of glass elements.
- **Shadows:** Use a single, very soft ambient shadow for floating buttons (FABs) and modals: `0 8px 32px rgba(0, 0, 0, 0.4)`.

## Shapes

The design system uses a **Rounded** language to soften the dark aesthetic and make it feel more "lifestyle" oriented.

- **Default Corner Radius:** 8px (0.5rem) for small components like input fields and buttons.
- **Large Corner Radius (rounded-lg):** 16px (1rem) for main restaurant cards and surface panels.
- **Extra Large Corner Radius (rounded-xl):** 24px (1.5rem) for bottom sheets and large promotional hero cards.
- **Pill:** Used exclusively for tags, chips, and budget segmented controls.

## Components

### Buttons & Inputs
- **Primary Button:** Solid Coral (#E23744) with white text. 8px radius.
- **Searchable Selects:** Surface color background with a 1px border. On focus, the border transitions to Primary Coral.
- **Segmented Budget Controls:** Pill-shaped toggle bar. Active state uses a slightly lighter surface tint (#25252E) with white text.

### Chips & Badges
- **Multi-select Chips:** Outlined style for inactive, solid Primary for active.
- **Rank Badges:** Circular or small pill shapes using Secondary Gold (#F5A623) to indicate "Top 10" or "AI Pick."

### Data Entry & Feedback
- **Rating Sliders:** Use a gradient track from Primary to Secondary. The handle should be a simple white circle.
- **Banners:** 
  - *Info:* Subtle blue tint border.
  - *Warning:* Secondary Gold border.
  - *Error:* Primary Coral border.
  - All banners use a desaturated version of their respective colors for the background at 10% opacity.

### Loading States
- **Skeleton Loaders:** Use a linear gradient animation moving from #1A1A22 to #25252E.