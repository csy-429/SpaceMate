---
name: Ethereal Logic
colors:
  surface: '#F8F7FB'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#494456'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#7a7487'
  outline-variant: '#cac3d8'
  surface-tint: '#6832eb'
  primary: '#540cd9'
  on-primary: '#ffffff'
  primary-container: '#6d3af1'
  on-primary-container: '#e6dcff'
  inverse-primary: '#cdbdff'
  secondary: '#ab3500'
  on-secondary: '#ffffff'
  secondary-container: '#fe6a34'
  on-secondary-container: '#5d1900'
  tertiary: '#005925'
  on-tertiary: '#ffffff'
  tertiary-container: '#007432'
  on-tertiary-container: '#6afe8e'
  error: '#EF4444'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e7deff'
  primary-fixed-dim: '#cdbdff'
  on-primary-fixed: '#20005f'
  on-primary-fixed-variant: '#4f00d0'
  secondary-fixed: '#ffdbd0'
  secondary-fixed-dim: '#ffb59d'
  on-secondary-fixed: '#390c00'
  on-secondary-fixed-variant: '#832600'
  tertiary-fixed: '#6bff8f'
  tertiary-fixed-dim: '#4ae176'
  on-tertiary-fixed: '#002109'
  on-tertiary-fixed-variant: '#005321'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
  border: '#E5E2ED'
  text-secondary: '#6B7280'
  brand-hover: '#5B2ED1'
  accent-yellow: '#FFD014'
typography:
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 17px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 20px
  caption:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1200px
  margin-x: 24px
  gutter: 16px
  stack-xs: 4px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
  stack-xl: 48px
---

## Brand & Style

The design system is built for a premium, AI-driven space-booking experience. The brand personality is **Modern, Trustworthy, and Tech-Forward**, prioritizing a "search-to-success" flow that feels effortless and intelligent.

The visual style is **Corporate / Modern** with a focus on high-clarity layouts, precision-engineered spacing, and a subtle infusion of **Glassmorphism** for navigational overlays to maintain a sense of space and transparency. The aesthetic relies on a clean, professional white-label feel that allows high-quality photography of venues to lead the visual narrative, supported by sharp typography and energetic accent colors to drive conversion.

## Colors

This color palette is designed for high functional contrast and brand recognition.

- **Primary (#6D3AF1):** Used for critical action paths, active states, and brand-focused UI elements. It conveys innovation and reliability.
- **Secondary (#FF6B35):** An "Urgency & Delight" color. Reserved for recommendations, discounts, and real-time availability ("NOW").
- **Surface & Background:** The system utilizes a layered white approach. `#FFFFFF` is used for the main canvas, while `#F8F7FB` (Surface) differentiates cards and footer sections to create depth without relying on heavy shadows.
- **Functional Neutrals:** Text utilizes a high-contrast primary gray for readability, while secondary text and borders use softer tones to manage information hierarchy and visual noise.

## Typography

The typography uses **Hanken Grotesk** to achieve a sharp, contemporary look that mirrors the precision of AI.

- **Hierarchy:** H1 and H2 levels are bold and tightly tracked for maximum impact. H3 is reserved for card titles and sub-headings to ensure a clear entry point for information scanning.
- **Legibility:** The body copy is set at 15px to balance density with readability, particularly important for space details and booking terms.
- **Utility:** Captions use the secondary text color and a smaller scale for meta-data, company info in the footer, and supporting labels.

## Layout & Spacing

The design system employs a **Fixed Grid** model for desktop, centered within a 1200px container.

- **The 4px Rhythm:** All spacing (padding, margins, component heights) must be a multiple of 4px. This ensures a mathematical harmony across the UI.
- **Header Architecture:** A 4-tier sticky header provides immediate access to navigation, search, and filtering. Each tier is separated by a 1px border (`#E5E2ED`).
- **Responsive Behavior:** On mobile, the 24px side margins are maintained, and the 4-tier header should condense into a 2-tier system (Logo/Nav + Search/Filter) with horizontal scrolling for categories.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layers** and **Ambient Shadows**.

- **Level 0 (Base):** `#FFFFFF` - The main background.
- **Level 1 (Subtle Surface):** `#F8F7FB` - Used for secondary content areas like the footer and background of card sections.
- **Level 2 (Cards/Floating):** White background with a soft ambient shadow (`0 2px 8px rgba(0,0,0,0.06)`). This is used to make venue cards and filter dropdowns "pop" from the base.
- **Level 3 (Sticky/Modals):** Elements like the sticky header use a background blur (10px) with 95% opacity to maintain context while scrolling.

## Shapes

The shape language is "Sophisticated Softness."

- **Standard Elements:** Buttons and input fields use an 8px radius (`rounded-md` equivalent) to feel approachable but professional.
- **Containers:** Venue cards use a 12px radius to soften the high-density grid.
- **Interactive Pill:** Specific interactive tags, such as category filters and "NOW" badges, use a full pill-shape (18px+) to distinguish them from functional action buttons.

## Components

- **Buttons:**
  - **Large CTA:** 48px height, Primary background, 8px radius. Used for "Book Now" or "Search."
  - **Medium:** 40px height, 8px radius. Used for secondary actions or internal card links.
- **Chips & Categories:**
  - Category chips are 36px in height with a pill radius. They feature a 24px icon followed by a label. Active state uses Primary color text and border.
- **Input Fields:**
  - Search dropdowns use the `#F8F7FB` surface with a 1px `#E5E2ED` border. On focus, the border transitions to Primary.
- **Cards:**
  - Cards feature a 16px internal padding. Images should have a top-rounded 12px radius to match the container. Metadata (price, location) uses H3 for titles and Body/Caption for details.
- **Badges:**
  - "NOW" and "Coupon" badges use the Accent color (`#FF6B35`) with white text to immediately draw the eye to value-added propositions.
