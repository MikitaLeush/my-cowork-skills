---
name: frontend-master
description: Use when generating or editing any frontend code (web or mobile) — components, pages, dashboards, animations, design systems, anything users see in a browser or native app. Load for React/Next.js, React Native/Expo, Tailwind/NativeWind, Framer Motion, Reanimated, GSAP. Also use when reviewing UI code, adding motion, polishing visuals, fixing layout, improving typography, designing color systems, or building interaction patterns. If there's even a 1% chance this touches the UI, load this skill.
---

# Frontend Master Skill

Three sources unified: **Emil Kowalski's animation craft** · **Impeccable design laws** · **High-agency aesthetic engineering**

---

## Context Detection — Read First

**Web** — React, Next.js, CSS, browser, Tailwind → focus `## Web` sections in loaded sub-skills

**Mobile (RN)** — React Native, Expo, NativeWind, Reanimated → focus `## Mobile (RN)` sections in loaded sub-skills

---

## Load When Relevant

| Task | Load |
|---|---|
| Any animation, motion, transition, gesture | [skills/emil-animation.md](skills/emil-animation.md) |
| Design laws, typography, color strategy, design audit | [skills/impeccable-design.md](skills/impeccable-design.md) |
| Creative direction, aesthetic, density dials, layout, React/RN architecture | [skills/taste-creative.md](skills/taste-creative.md) |
| Full build — page or screen from scratch | All 3 |
| Reviewing / polishing / auditing existing UI | [skills/impeccable-design.md](skills/impeccable-design.md) + [skills/taste-creative.md](skills/taste-creative.md) |

---

## Core Philosophy (Always Active)

**Taste is trained, not innate.** Study why great interfaces feel the way they do. Reverse-engineer animations. Be curious.

**Unseen details compound.** Users never consciously notice most details. That is the point. The aggregate of invisible correctness creates interfaces people love without knowing why.

**Beauty is leverage.** In a world where software is "good enough," taste is the differentiator.

**Never generate the same aesthetic twice.** Vary layout archetypes, color strategies, vibe profiles. Failure: someone can guess your theme + palette from the category alone.

---

## Absolute Bans (Always Active — Match and Refuse)

### Fonts
**Banned:** `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`
**Use instead:** `Geist`, `Satoshi`, `Cabinet Grotesk`, `Outfit`, `Plus Jakarta Sans`, `Clash Display`, `PP Editorial New`

### Color
- `#000` / `#fff` — tint neutrals toward brand hue (OKLCH chroma 0.005–0.01)
- AI-purple / blue neon glow aesthetic
- Gradient text (`background-clip: text`) — solid color + weight/size instead
- Glassmorphism as default decor — rare and purposeful only

### Layout & Structure
- Centered H1 hero on creative work — Split Screen, Left-Aligned, or Asymmetric
- Identical 3-column equal card grids — use Zig-Zag, asymmetric, or horizontal scroll
- Nested cards (always wrong)
- `h-screen` on full-height sections — always `min-h-[100dvh]` (iOS Safari) / `flex: 1` (RN)
- Side-stripe `border-left`/`border-right` > 1px as accent

### Animation
- `transition: all` — specify exact properties
- `scale(0)` entry — use `scale(0.95)` + opacity
- `ease-in` on any UI element
- Duration > 300ms on standard UI (tooltip, dropdown, button)
- `linear`/`ease-in-out` on interactive elements — use custom cubic-beziers
- Animating `top`, `left`, `width`, `height` — only `transform` + `opacity`
- `window.addEventListener('scroll')` — use `IntersectionObserver` or Framer `whileInView`

### Content
- Generic names: "John Doe", "Acme", "Nexus", "SmartFlow"
- Round fake numbers: `50%`, `99.99%` — use organic: `47.2%`, `+1 (312) 847-1928`
- Copy clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Delve"
- Emojis in code, markup, or text — replace with icons or SVG primitives
- Unsplash URLs — use `https://picsum.photos/seed/{context}/800/600`
- Hero-metric template (big number + gradient accent) — SaaS cliché

---

## AI Slop Test (Always Run Before Delivering)

1. **First-order:** Can someone guess theme + palette from category alone? ("healthcare → white + teal") → rework
2. **Second-order:** Can someone guess aesthetic family from category + anti-references? → rework until both non-obvious

---

## Pre-flight Checklist

- [ ] No banned fonts, icons, shadows, layouts, or motion patterns
- [ ] Color strategy explicitly chosen — not defaulted to Restrained
- [ ] Dark/light decided by physical scene sentence
- [ ] Web: `min-h-[100dvh]` — never `h-screen` · Mobile: `flex: 1` with safe area insets
- [ ] Mobile collapse guaranteed (`w-full px-4`) for asymmetric web layouts
- [ ] Custom cubic-bezier transitions — no `linear` or `ease-in-out`
- [ ] Entry animations present — no element appears statically
- [ ] Only `transform` + `opacity` animated
- [ ] `backdrop-blur` only on fixed/sticky — never scrolling content
- [ ] Loading, empty, and error states implemented
- [ ] All third-party imports verified against `package.json`
- [ ] Organic data — no generic names, round numbers, copy clichés
- [ ] AI slop test passed (first AND second order)
