# Impeccable Design
*Source: pbakaus/impeccable — production-grade design system*

Design laws, color strategy, typography, layout, and the full impeccable command system. Web section covers browser/CSS contexts. Mobile section covers React Native adaptations. Deep reference files remain at their original location — load them when doing focused deep work.

---

## Web

### Color System

#### Use OKLCH
Reduce chroma as lightness approaches 0 or 100 — high chroma at extremes looks garish.

Never `#000` or `#fff`. Tint every neutral toward brand hue (chroma 0.005–0.01 is enough to feel intentional).

#### Color Strategy — pick before picking colors

**Restrained** — Tinted neutrals + one accent ≤10% of surface. Product default. Safe but never an excuse for laziness.

**Committed** — One saturated color carries 30–60% of surface. Correct default for identity-driven brand pages. The "one accent ≤10%" rule does NOT apply here.

**Full palette** — 3–4 named roles, each used deliberately. Brand campaigns, product data viz.

**Drenched** — Surface IS the color. Brand heroes, campaign pages, emotional moments.

The "one accent ≤10%" rule is Restrained only. Committed/Full/Drenched exceed it on purpose. Don't collapse every design to Restrained by reflex.

**The AI-purple ban:** No purple button glows, no neon gradients. Use absolute neutral bases (Zinc/Slate) with singular accents: Emerald, Electric Blue, Deep Rose. Never mix warm and cool grays in the same project.

#### Warm Monochrome (editorial/minimalist contexts)
- Canvas: `#FFFFFF` or `#F7F6F3`
- Borders/dividers: `#EAEAEA` or `rgba(0,0,0,0.06)`
- Body text: `#111111` or `#2F3437` — never pure black
- Secondary text: `#787774`
- Muted pastels for semantic tags: Pale Red `#FDEBEC/text #9F2F2D`, Pale Blue `#E1F3FE/text #1F6C9F`, Pale Green `#EDF3EC/text #346538`, Pale Yellow `#FBF3DB/text #956400`

---

### Theme Decision

Dark vs. light is never a default. **Write one physical scene sentence before choosing.** It must force the answer:
- "SRE glancing at incident severity on a 27-inch monitor at 2am in a dim room" → forces dark
- "Designer reviewing visual assets in a bright studio at noon" → forces light
- "Observability dashboard" → does NOT force answer. Add detail until it does.

---

### Typography

**Scale:**
- Headline: `text-4xl md:text-6xl tracking-tighter leading-none`
- Body: `text-base leading-relaxed max-w-[65ch]`
- Body line length: 65–75ch max
- Hierarchy: scale + weight contrast ≥1.25 ratio between steps

**Fonts by context:**
- **Product/dashboard/tool UI:** `Geist` + `Geist Mono`, `Satoshi` + `JetBrains Mono`
- **Creative/editorial/landing:** `Lyon Text`, `Newsreader`, `Playfair Display`, `Instrument Serif` — apply `letter-spacing: -0.02em` to `-0.04em`, `line-height: 1.1`
- **Code/keystrokes/metadata:** `Geist Mono`, `SF Mono`, `JetBrains Mono`
- **Banned:** `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica` — all contexts

**Headlines:** Don't make H1 scream — control hierarchy through weight + color, not just massive scale. Eyebrow tags: `rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium`

---

### Layout

- Section padding minimum: `py-24` (agency-tier: `py-24` to `py-40`)
- Page constraint: `max-w-[1400px] mx-auto` or `max-w-7xl`
- Content width: `max-w-4xl` or `max-w-5xl` for body text
- Internal card padding: `p-8` or `p-10`
- **Grid over flex-math:** Never `w-[calc(33%-1rem)]` → always `grid grid-cols-1 md:grid-cols-3 gap-6`
- **Anti-center bias:** Centered hero banned for creative work — Force Split Screen, Left-Aligned, or Asymmetric
- Edge-to-edge sticky navbar → use floating glass pill: `mt-6 mx-auto w-max rounded-full`

**Cards:** Use only when elevation communicates hierarchy. Shadow tinted to background hue — never generic dark drop shadows. Nested cards are always wrong.

**Mobile web responsive:** Any asymmetric layout must collapse to `w-full px-4 py-8` below 768px. Remove all rotations and negative-margin overlaps.

---

### Copy Rules

- Every word earns its place. No restated headings, no intros that repeat the title.
- No em dashes — use commas, colons, semicolons, periods, or parentheses.
- No AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve"
- Use concrete verbs, not abstract startup language.

---

### Register: Brand vs Product

Every design task is one of two registers — identify before designing:

**Brand** — Marketing, landing, campaign, long-form content. Design IS the product. More expressive color, editorial typography allowed, drenched/committed strategies.

**Product** — App UI, admin, dashboard, tool. Design SERVES the product. Restrained color, functional hierarchy, no serif on key UI elements.

Priority: (1) cue in the task text → (2) surface in focus → (3) project context. First match wins.

---

### Component Specifications

| Component | Spec |
|---|---|
| Card border | `1px solid #EAEAEA`, `border-radius: 8px–12px` |
| Primary CTA (minimal) | `bg-[#111111] text-white`, `border-radius: 4px–6px`, no box-shadow |
| Tags / status badges | `rounded-full text-xs uppercase tracking-[0.05em]`, muted pastels only |
| Accordions | Strip container boxes. `border-bottom: 1px solid #EAEAEA` only |
| Keystroke UI | `<kbd style="border:1px solid #EAEAEA; border-radius:4px; background:#F7F6F3; font-family:monospace">` |

---

### Heuristic Scoring (critique/audit mode)

Score across: Clarity · Hierarchy · Consistency · Feedback · Error Prevention · Efficiency · Aesthetics · Accessibility

---

### Impeccable Command Reference

| Command | What it does |
|---|---|
| `craft` | Shape, then build a feature end-to-end |
| `shape` | Plan UX/UI before writing code |
| `critique` | UX review with heuristic scoring |
| `audit` | Technical checks (a11y, perf, responsive) |
| `polish` | Final quality pass before shipping |
| `bolder` | Amplify safe or bland designs |
| `quieter` | Tone down aggressive/overstimulating designs |
| `distill` | Strip to essence, remove complexity |
| `harden` | Production-ready: errors, i18n, edge cases |
| `onboard` | First-run flows, empty states, activation |
| `animate` | Add purposeful animations and motion |
| `colorize` | Add strategic color to monochromatic UIs |
| `typeset` | Improve typography hierarchy and fonts |
| `layout` | Fix spacing, rhythm, visual hierarchy |
| `delight` | Add personality and memorable touches |
| `overdrive` | Push past conventional limits |
| `clarify` | Improve UX copy, labels, error messages |
| `adapt` | Adapt for different devices/screen sizes |
| `optimize` | Diagnose and fix UI performance |

---

### Impeccable Deep-Reference Map

Load these when doing focused deep work — they contain exhaustive technique details:

| Load when... | File |
|---|---|
| Animation iteration via impeccable | `impeccable/reference/animate.md` |
| Typography deep work | `impeccable/reference/typography.md` |
| Color system | `impeccable/reference/color-and-contrast.md` |
| Visual craft / detailing | `impeccable/reference/craft.md` |
| Design audit | `impeccable/reference/audit.md` |
| Layout system | `impeccable/reference/layout.md` |
| Interaction design | `impeccable/reference/interaction-design.md` |
| Motion design (impeccable lens) | `impeccable/reference/motion-design.md` |
| Live browser editing session | `impeccable/reference/live.md` |
| Cognitive load reduction | `impeccable/reference/cognitive-load.md` |
| Responsive design | `impeccable/reference/responsive-design.md` |
| Spatial design | `impeccable/reference/spatial-design.md` |
| Visual asset generation | use agent → `impeccable/agents/impeccable-asset-producer.md` |

---

## Mobile (RN)

### Touch Targets

- **iOS minimum:** 44×44pt (Human Interface Guidelines)
- **Android minimum:** 48×48dp (Material Design)
- `hitSlop` to expand touch area without changing visual size:
```jsx
<TouchableOpacity hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
```

---

### Safe Area

Always wrap screens in safe area context — accounts for notch, Dynamic Island, home indicator:

```jsx
import { SafeAreaView } from 'react-native-safe-area-context';
<SafeAreaView style={{ flex: 1 }}>

// Or insets for custom positioning
import { useSafeAreaInsets } from 'react-native-safe-area-context';
const insets = useSafeAreaInsets();
<View style={{ paddingTop: insets.top, paddingBottom: insets.bottom }}>
```

---

### Typography Scale (RN)

| Role | Size | Notes |
|---|---|---|
| Display / hero | 34–48sp | `fontWeight: '700'` or `'800'` |
| Headline | 24–30sp | `fontWeight: '600'` |
| Title | 18–22sp | `fontWeight: '600'` |
| Body | 15–16sp | `fontWeight: '400'`, `lineHeight: 24` |
| Caption | 12–13sp | **Never below 12sp** |
| Mono / code | 13–14sp | system mono |

**Banned fonts still apply.** System fonts (`-apple-system` on iOS, `Roboto` on Android) allowed as last resort only. Custom fonts require `expo-font` or `@expo-google-fonts`.

**letterSpacing in RN is in points, not em:**
- CSS `letter-spacing: -0.02em` at 16px ≈ RN `letterSpacing: -0.32`
- Scale: CSS_em_value × font_size_in_points = RN_letterSpacing

---

### Platform-Specific Design

```jsx
import { Platform } from 'react-native';

// Font weight behaves differently — test both
Platform.OS === 'ios'
  ? { fontWeight: '600' }  // iOS: renders visibly between 400 and 700
  : { fontWeight: '700' }  // Android: 600 often renders same as 400

// Shadows
const shadowStyle = Platform.select({
  ios: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
  },
  android: {
    elevation: 4,
  },
});
```

---

### Color Strategy (RN)

Same Restrained / Committed / Full / Drenched strategies apply. Additional considerations:
- **Dark mode:** `useColorScheme()` from `react-native` or `Appearance.getColorScheme()`
- OLED screens on mobile: true black `#000000` for dark backgrounds (saves battery, looks premium)
- Tinted neutrals still apply for non-OLED dark themes

```jsx
import { useColorScheme } from 'react-native';
const colorScheme = useColorScheme(); // 'light' | 'dark' | null
```

---

### NativeWind

NativeWind v4 maps Tailwind classes to RN StyleSheets. Key differences from web:
- No `hover:`, `focus:`, `active:` — use `Pressable` with `pressed` state
- No CSS Grid — use Flexbox layout only
- `min-h-[100dvh]` → use `flex: 1` with SafeAreaView
- Animations: NativeWind has no animation utilities — use Reanimated directly

```jsx
// Pressable with active state
<Pressable className="bg-slate-900 rounded-lg px-4 py-3"
  style={({ pressed }) => pressed && { opacity: 0.8, transform: [{ scale: 0.98 }] }}>
  <Text className="text-white font-semibold">Button</Text>
</Pressable>
```

---

### Impeccable Commands in RN Context

All commands work — just generate React Native / NativeWind code instead of HTML/Tailwind:
- `craft` → generates RN Screen with proper SafeAreaView, FlatList, Pressable, Reanimated
- `audit` → checks: touch targets, safe areas, keyboard avoidance, font sizes, a11y labels
- `adapt` → focuses on iOS vs Android platform differences
- `harden` → adds `accessibilityLabel`, `accessibilityRole`, keyboard avoidance (`KeyboardAvoidingView`)
