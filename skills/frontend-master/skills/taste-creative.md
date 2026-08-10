# Taste Creative
*Source: Leonxlnx/taste-skill — high-agency aesthetic engineering*

Creative direction, vibe archetypes, design dials, layout patterns, and React/RN component architecture. Web section covers browser/CSS. Mobile section covers React Native layout and aesthetic adaptation.

---

## Web

### Design Dials — Active Baseline

```
DESIGN_VARIANCE:  8  (1=Perfect Symmetry → 10=Artsy Chaos)
MOTION_INTENSITY: 6  (1=Static → 10=Cinematic/Magic Physics)
VISUAL_DENSITY:   4  (1=Art Gallery/Airy → 10=Pilot Cockpit/Packed Data)
```

Always listen to user — adapt dynamically based on explicit prompt.

---

### DESIGN_VARIANCE Detail

| Level | Behavior |
|---|---|
| 1–3 | Flexbox `justify-center`, strict 12-col symmetrical grids, equal paddings, all hero center-aligned |
| 4–7 | `margin-top: -2rem` overlapping elements, varied image aspect ratios, left-aligned headers over center-aligned data, mixed section padding, 2-column Zig-Zag rows |
| 8–10 | Masonry layouts, `grid-template-columns: 2fr 1fr 1fr`, massive empty zones (`padding-left: 20vw`), off-axis typography, overlapping z-index depth, Z-axis cascade |

**Mobile override for 4–10:** ANY asymmetric layout above `md:` MUST collapse to `w-full px-4 py-8` below 768px. Remove all rotations and negative-margin overlaps. Single-column stack only.

---

### MOTION_INTENSITY Detail

| Level | Behavior |
|---|---|
| 1–3 | No automatic animations. CSS `:hover` + `:active` states only. Instant state changes. |
| 4–7 | `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)` on interactive elements. Load-in `animation-delay` cascades. `IntersectionObserver` for scroll-triggered reveals. Only `transform` + `opacity`. |
| 8–10 | Complex scroll-triggered reveals (`whileInView`/`IntersectionObserver`). Parallax. Framer hooks (`useScroll`, `useTransform`, `useSpring`). Magnetic cursor-pull. Perpetual micro-interactions. Spring physics on all interactive elements. Layout transitions with `layout` + `layoutId`. GSAP/ThreeJS for canvas. |

When MOTION_INTENSITY > 5:
- Add perpetual micro-interactions (Pulse, Typewriter, Float, Shimmer) to all major components
- Spring physics on all interactive elements: `{ type: "spring", stiffness: 100, damping: 20 }`

---

### VISUAL_DENSITY Detail

| Level | Behavior |
|---|---|
| 1–3 | **Art Gallery Mode:** `py-32` to `py-48` section gaps. Very few elements per view. Expensive and clean. Hero: one headline, one CTA, nothing else. |
| 4–7 | **Daily App Mode:** `py-16` to `py-24` section gaps. Cards with `p-6` to `p-8`. 3–5 content elements per section. |
| 8–10 | **Cockpit Mode:** `p-2` to `p-4` inside containers. No card boxes — `border-t`, `divide-y`, negative space only. `font-mono` for all numbers. Bloomberg terminal / Figma devtools level. |

At VISUAL_DENSITY > 7: generic card containers BANNED.

---

### Vibe Archetypes — Pick One Per Project

Never generate the same aesthetic twice. Roll based on context.

#### Ethereal Glass (SaaS / AI / Tech)
- Background: Deepest OLED black `#050505`, radial mesh gradients (subtle glowing purple/emerald orbs)
- Cards: Vantablack with heavy `backdrop-blur-2xl`, pure `white/10` hairline borders
- Typography: Wide geometric Grotesk fonts
- Mood: Cold, precise, powerful

#### Editorial Luxury (Lifestyle / Real Estate / Agency)
- Background: Warm creams `#FDFBF7`, muted sage, or deep espresso
- Typography: High-contrast Variable Serif for massive headings
- Texture: Subtle CSS noise/film-grain overlay (`opacity-[0.03]`) for physical paper feel
- Mood: Expensive, tactile, human

#### Soft Structuralism (Consumer / Health / Portfolio)
- Background: Silver-grey or pure white
- Typography: Massive bold Grotesk
- Components: Airy, floating — unbelievably soft, highly diffused ambient shadows
- Mood: Clean, open, trustworthy

---

### Vibe Selection Guide

| Context | Vibe | Color strategy | Font pairing |
|---|---|---|---|
| SaaS / AI / B2B Tech | Ethereal Glass | Committed dark | Geist + Geist Mono |
| Lifestyle / Fashion / Real Estate | Editorial Luxury | Drenched or Full | Serif + Satoshi |
| Health / Consumer / Portfolio | Soft Structuralism | Restrained or Committed | Satoshi + Instrument Serif |
| Developer Tool / CLI | Cockpit (density 8–10) | Restrained dark | Geist Mono + Geist |
| Agency / Creative Studio | Editorial Split | Full or Drenched | Clash Display + Satoshi |
| Data Dashboard / Analytics | Cockpit or Structuralism | Committed (data colors) | Geist + Geist Mono |
| Marketing / Campaign | Drenched hero + Restrained body | Committed | Cabinet Grotesk + Newsreader |

---

### The Category-Reflex Trap

**First-order reflex** (obvious): If theme + palette guessable from category alone → rework:
- "Observability" → dark blue · "Healthcare" → white + teal · "Finance" → navy + gold · "Crypto" → neon on black

**Second-order reflex** (subtle): If aesthetic family guessable from category + anti-references → rework:
- "AI tool that's not SaaS-cream" → editorial-typographic — if you landed here by elimination, CAUGHT

Both levels must be non-obvious before delivery.

---

### Layout Archetypes

#### The Asymmetric Bento
```css
.grid { display: grid; grid-template-columns: repeat(12, 1fr); }
.card-wide  { grid-column: span 8; grid-row: span 2; }
.card-stack { grid-column: span 4; }
/* Mobile: all → grid-column: span 12 */
```

#### The Z-Axis Cascade
Elements stacked like physical cards, slightly overlapping with varying depth. Subtle rotation (`-2deg`/`3deg`). Mobile: remove all rotations/negative-margin overlaps, stack vertically.

#### The Editorial Split
Massive typography left half (`w-1/2`). Interactive scrollable content right. Mobile: full-width vertical stack.

---

### Premium Component Patterns

#### The Double-Bezel (Doppelrand)
```jsx
<div className="bg-black/5 ring-1 ring-black/5 p-1.5 rounded-[2rem]">
  <div className="bg-white shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)] rounded-[calc(2rem-0.375rem)] p-8">
    {children}
  </div>
</div>
```

#### Button-in-Button Icon Architecture
```jsx
<button className="flex items-center gap-2 px-6 py-3 rounded-full bg-black text-white">
  Get started
  <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">↗</span>
</button>
```

#### Floating Glass Pill Nav
```jsx
<nav className="fixed top-6 left-1/2 -translate-x-1/2 w-max rounded-full
  bg-white/10 backdrop-blur-xl border border-white/20 px-6 py-3">
```

#### Hamburger Morph to X
```jsx
<span className={`block w-6 h-px bg-current transition-all duration-300 ${open ? 'rotate-45 translate-y-px' : '-translate-y-1'}`} />
<span className={`block w-6 h-px bg-current transition-all duration-300 ${open ? '-rotate-45' : 'translate-y-1'}`} />
```

#### Magnetic Button (Framer Motion)
```jsx
// CRITICAL: useMotionValue + useTransform, NEVER useState for continuous motion
const x = useMotionValue(0);
const y = useMotionValue(0);
const rotateX = useTransform(y, [-0.5, 0.5], [7, -7]);
const rotateY = useTransform(x, [-0.5, 0.5], [-7, 7]);
```

---

### Pattern Arsenal

#### Navigation
| Pattern | Description |
|---|---|
| Mac OS Dock Magnification | Nav icons scale fluidly on hover |
| Magnetic Button | Buttons physically pull toward cursor |
| Dynamic Island | Pill-shaped UI morphs to show status |
| Floating Speed Dial | FAB springs into curved secondary actions |
| Mega Menu Reveal | Full-screen dropdown with staggered content |

#### Layout & Grid
| Pattern | Description |
|---|---|
| Bento Grid | Asymmetric tile-based (Apple Control Center) |
| Masonry Layout | Staggered grid, no fixed row heights |
| Chroma Grid | Grid tiles with continuously animating color gradients |
| Split Screen Scroll | Two halves sliding opposite directions on scroll |
| Curtain Reveal | Hero parting like curtain on scroll |

#### Cards
| Pattern | Description |
|---|---|
| Parallax Tilt Card | 3D-tilting card tracking mouse coordinates |
| Spotlight Border Card | Card borders illuminate dynamically under cursor |
| Morphing Modal | Button seamlessly expands into full-screen dialog |

#### Scroll
| Pattern | Description |
|---|---|
| Sticky Scroll Stack | Cards stick to top and stack over each other |
| Horizontal Scroll Hijack | Vertical scroll → smooth horizontal gallery pan |
| Zoom Parallax | Central background image zooms on scroll |
| Scroll Progress Path | SVG lines draw themselves as user scrolls |

#### Text Effects
| Pattern | Description |
|---|---|
| Kinetic Marquee | Endless text bands reversing direction on scroll |
| Text Mask Reveal | Massive type as transparent window to video bg |
| Text Scramble | Matrix-style character decoding on load/hover |
| Gradient Stroke Animation | Outlined text with gradient running along stroke |

#### Micro-Interactions
| Pattern | Description |
|---|---|
| Particle Explosion Button | CTAs shatter into particles on success |
| Skeleton Shimmer | Shifting light across placeholder boxes |
| Directional Hover Fill | Fill enters from exact side mouse entered |
| Mesh Gradient Background | Lava-lamp animated color blobs |

---

### The Bento Motion Engine (SaaS Dashboards)

**Core:** "Vercel-core meets Dribbble-clean" — perpetual physics, not static cards.

**Palette:** `#f9fafb` bg · `#ffffff` cards with `border-slate-200/50` · `rounded-[2.5rem]` · `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]` · `Geist`/`Satoshi`/`Cabinet Grotesk` with `tracking-tight`

**Animation:** `type: "spring", stiffness: 100, damping: 20` · `layout` + `layoutId` props · Every card has infinite loop active state (Pulse/Typewriter/Float/Carousel) · **CRITICAL:** Perpetual motion MUST be memoized (`React.memo`) in isolated Client Component.

**The 5 Card Archetypes:**
1. **Intelligent List** — Vertical stack, infinite auto-sort via `layoutId`, simulates AI prioritizing
2. **Command Input** — AI bar with Typewriter, blinking cursor, shimmer loading
3. **Live Status** — Breathing indicators + overshoot spring notification badge
4. **Wide Data Stream** — Seamless horizontal carousel `x: ["0%", "-100%"]`
5. **Focus Mode** — Document view with staggered text highlight → float-in action toolbar

---

### Scroll Entry Animation (Universal)

Every element entering the viewport:
```jsx
// Framer Motion
<motion.div
  initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
  whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
  viewport={{ once: true, margin: "-80px" }}
  transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
>
```

Never use `window.addEventListener('scroll')`.

---

### Glass Effect (Purposeful)

```css
.glass-panel {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
```

Only apply `backdrop-blur` to fixed/sticky elements. Never to scrolling containers.

---

### Component Architecture (React / Next.js)

**Framework defaults:** React or Next.js with Server Components (RSC).

**RSC Safety:**
- Global state ONLY in Client Components
- Framer Motion hooks → extract as isolated leaf `'use client'` component
- Server Components render static layouts only

**State:** `useState`/`useReducer` for isolated UI. NEVER `useState` for magnetic hover or continuous animations — use `useMotionValue` + `useTransform`.

**Tailwind version lock:** Check `package.json` first. v3: don't use v4 syntax. v4: use `@tailwindcss/postcss` not `tailwindcss` in postcss.config.

**Icons:** `@phosphor-icons/react` (Light/Bold) or `@radix-ui/react-icons`. Banned: Lucide default, FontAwesome, Material Icons. Standardize `strokeWidth` globally (1.5 or 2.0).

**Dependency verification (MANDATORY):** Before importing any third-party library, check `package.json`. If missing → output install command first. Never assume a library exists.

---

### Mandatory Interaction States

LLMs naturally generate only "static success" states. Always implement:

**Loading:** Skeletal loaders matching layout dimensions — no generic circular spinners.
```jsx
<div className="animate-pulse">
  <div className="h-6 bg-slate-200 rounded w-3/4 mb-3" />
  <div className="h-4 bg-slate-200 rounded w-1/2" />
</div>
```

**Empty State:** Beautifully composed — indicates clearly how to populate data.

**Error State:** Inline, clear, specific. Never "Something went wrong."

**Tactile Feedback:**
```jsx
<button className="active:scale-[0.98] active:-translate-y-[1px] transition-transform duration-100">
```

---

### Form Patterns

- Label **above** input — never inline placeholder as label
- Error text: below input, inline
```jsx
<div className="flex flex-col gap-2">
  <label className="text-sm font-medium text-slate-700">Email</label>
  <input className="..." />
  <p className="text-xs text-slate-500">Helper text</p>
  {error && <p className="text-xs text-red-600">{error}</p>}
</div>
```

---

### Framer Motion Patterns

**Stagger orchestration:**
```jsx
const listVariants = { show: { transition: { staggerChildren: 0.08 } } };
const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 20 } }
};
<motion.ul variants={listVariants} initial="hidden" animate="show">
  {items.map(item => <motion.li key={item.id} variants={itemVariants}>{item}</motion.li>)}
</motion.ul>
```

**Layout transitions:** `<motion.div layout layoutId="card-{id}">` for smooth re-ordering.

**AnimatePresence:**
```jsx
<AnimatePresence>
  {items.map(item => (
    <motion.div key={item.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {item}
    </motion.div>
  ))}
</AnimatePresence>
```

**Perpetual micro-animation isolation:**
```jsx
const PulsingDot = memo(function PulsingDot() {
  return (
    <motion.div className="w-2 h-2 rounded-full bg-green-400"
      animate={{ scale: [1, 1.4, 1], opacity: [1, 0.7, 1] }}
      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
    />
  );
});
```

---

### Performance Rules

- GPU-safe only: `transform` + `opacity`, never `height`/`padding`/`top`
- `backdrop-blur` only on fixed/sticky elements — never scrolling containers
- `will-change: transform` sparingly, only on actively animating elements — remove after
- Never arbitrary `z-50` or `z-[9999]` — reserve for systemic layers (nav, modals, overlays, tooltips)
- Grain/noise: `position: fixed; pointer-events: none` pseudo-element only

---

### GSAP / ThreeJS Rules

- GSAP (ScrollTrigger/Parallax) for complex scrolltelling or parallax sequences
- ThreeJS/WebGL for 3D/Canvas animations — never for UI elements
- **NEVER mix GSAP/ThreeJS with Framer Motion in same component tree**
- Always cleanup:
```jsx
useEffect(() => {
  const ctx = gsap.context(() => { /* animations */ }, ref);
  return () => ctx.revert();
}, []);
```

---

### Agency Execution Protocol

When generating UI at high DESIGN_VARIANCE + MOTION_INTENSITY:

1. **[SILENT] Roll Variance Engine** — choose vibe archetype + layout archetype, ensure unique combo
2. **[SCAFFOLD]** — background texture, macro-whitespace scale, massive typography sizes, color strategy
3. **[ARCHITECT]** — Double-Bezel for all major cards, `rounded-[2rem]`, `min-h-[100dvh]`, CSS Grid structure
4. **[CHOREOGRAPH]** — custom `cubic-bezier` transitions, staggered reveals, scroll entry animations
5. **[OUTPUT]** — flawless React/Tailwind code, no generic fallbacks, all banned patterns absent, pre-flight verified

---

## Mobile (RN)

### Layout System — Flexbox Only

RN has no CSS Grid. Everything is Flexbox. Key patterns:

```jsx
// Full-screen layout
<View style={{ flex: 1 }}>

// Horizontal stack
<View style={{ flexDirection: 'row', alignItems: 'center' }}>

// Grid-like with wrap (replaces CSS grid)
<View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
  {items.map(item => (
    <View style={{ width: '50%', padding: 8 }}>{item}</View>
  ))}
</View>

// With NativeWind
<View className="flex-1">
<View className="flex-row items-center">
<View className="flex-row flex-wrap">
```

---

### RN Spacing Scale

Use 4-point rhythm (avoids sub-pixel rendering):
```
4, 8, 12, 16, 20, 24, 32, 40, 48, 64
```

**Account for device chrome when planning layout:**
- iOS Status Bar: ~44pt
- Android Status Bar: ~24dp (varies by device)
- Bottom Tab Bar: ~80pt (add insets.bottom)
- Home Indicator (iPhone): ~34pt — covered by SafeAreaView

---

### RN Vibe Archetypes

Same 3 vibes, adapted for native:

**Ethereal Glass (RN):**
- Dark bg: `backgroundColor: '#050505'` or `'#0a0a0a'`
- Glass effect: `BlurView` from `expo-blur` (not CSS `backdrop-filter`)
- OLED black is premium on mobile — use `#000000` for pure dark bg
- Cards: dark surface `#111111` with thin `rgba(255,255,255,0.08)` borders

**Editorial Luxury (RN):**
- Warm cream bg still works: `#FDFBF7`
- Custom fonts via `expo-font` or `@expo-google-fonts`
- Texture: not achievable natively — use subtle image with low opacity overlay

**Soft Structuralism (RN):**
- White/light grey backgrounds: `#FFFFFF`, `#F8F9FA`
- Shadow adapted (see platform-specific shadows in impeccable-design.md)
- Rounded corners: `borderRadius: 16–24` (not `rounded-[2rem]`)

---

### Design Dials in RN

**VISUAL_DENSITY in RN:**
| Level | RN Behavior |
|---|---|
| 1–3 (Art Gallery) | Large `paddingVertical: 48–64`, one content item per screen section, `fontSize: 34+` for headlines |
| 4–7 (Daily App) | Standard `padding: 16–24`, normal list density, `FlatList` with `itemSeparatorComponent` |
| 8–10 (Cockpit) | `padding: 4–8`, no `Card` wrappers, `View` with `borderBottomWidth: 1`, `fontFamily: 'monospace'` for all numbers |

**MOTION_INTENSITY in RN:**
| Level | RN Behavior |
|---|---|
| 1–3 | Pressable with instant `opacity` change only |
| 4–7 | Reanimated `withTiming` transitions, `useAnimatedStyle` for smooth state changes |
| 8–10 | `withSpring` on all interactive elements, Moti stagger, Layout Animations, gesture-driven motion |

---

### NativeWind vs StyleSheet.create

**Use NativeWind when:**
- Rapid iteration, prototyping
- Team familiar with Tailwind
- Responsive adjustments needed (`sm:`, `md:` breakpoints via RN dimensions)

**Use StyleSheet.create when:**
- Performance-critical components (list cells, high-frequency renders)
- Platform-specific splits needed (`Platform.select`)
- Complex conditional styles that get messy as class strings

**Both can coexist** — NativeWind for layout/typography, StyleSheet for animations and platform splits.

---

### ScrollView vs FlatList

- **ScrollView:** forms, content pages, settings screens — small, known content
- **FlatList:** any list > ~20 items — virtualized, renders only visible items
- **SectionList:** FlatList with section headers
- Never render 100+ items in a ScrollView — kills performance

```jsx
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <ItemComponent item={item} />}
  ItemSeparatorComponent={() => <View className="border-b border-slate-200/50" />}
  contentContainerStyle={{ paddingBottom: insets.bottom + 80 }}
/>
```

---

### Mandatory Interaction States (RN)

Same as web — always implement:

**Loading:** Use `ContentLoader` (react-content-loader) or manual skeleton with Reanimated shimmer
**Empty State:** Clear illustration + CTA button to populate
**Error:** Inline, specific — never "Something went wrong"
**Haptic feedback on key actions:** `expo-haptics` (see emil-animation.md mobile section)

---

### RN Production Standards

- `accessibilityLabel` on every interactive element without visible text
- `accessibilityRole` on custom interactive components (`"button"`, `"link"`, `"checkbox"`)
- `KeyboardAvoidingView` on all screens with text inputs
- No `console.log` in production — use `__DEV__` guard
- TypeScript strict mode — no `any` types
- `useCallback` for FlatList `renderItem` — prevents unnecessary re-renders
