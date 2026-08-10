# Emil Animation
*Source: emilkowalski/skill — design engineering philosophy*

Animation craft for both browser and native app surfaces. Web section covers CSS, Framer Motion, GSAP. Mobile section covers Reanimated 3, Moti, and gesture handler.

---

## Web

### The Decision Framework

#### 1. Should it animate at all?

| Frequency | Decision |
|---|---|
| 100+ times/day (keyboard, command palette) | **No animation. Ever.** |
| Tens of times/day (hover, list nav) | Remove or drastically reduce |
| Occasional (modals, drawers, toasts) | Standard animation |
| Rare/first-time (onboarding, celebrations) | Can add delight |

**Never animate keyboard-initiated actions.** Raycast has no open/close animation — that is optimal for something used hundreds of times daily.

#### 2. What is the purpose?

Every animation must answer "why does this animate?" Valid purposes:
- **Spatial consistency** — toast enters/exits same direction, swipe-to-dismiss feels intuitive
- **State indication** — morphing feedback button shows state change
- **Explanation** — marketing animation showing how a feature works
- **Feedback** — button scales on press, confirming the UI heard the user
- **Preventing jarring changes** — elements appearing without transition feel broken

Purpose is "it looks cool" AND users see it often → don't animate.

#### 3. What easing?

```
Entering or exiting element     → ease-out    (starts fast, feels responsive)
Moving / morphing on screen     → ease-in-out (natural arc)
Hover / color change            → ease
Constant motion (marquee)       → linear
Default                         → ease-out
```

**Never ease-in on UI** — starts slow, delays exactly when user is watching.

**Always use custom curves — built-in CSS easings are too weak:**
```css
--ease-out:     cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out:  cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer:  cubic-bezier(0.32, 0.72, 0, 1);   /* iOS-like */
--ease-ui:      cubic-bezier(0.16, 1, 0.3, 1);    /* agency heavy */
```

Resources: [easing.dev](https://easing.dev/) · [easings.co](https://easings.co/)

#### 4. How fast?

| Element | Duration |
|---|---|
| Button press feedback | 100–160ms |
| Tooltips, small popovers | 125–200ms |
| Dropdowns, selects | 150–250ms |
| Modals, drawers | 200–500ms |
| Scroll entry reveals | 600–800ms |
| Marketing/explanatory | Can be longer |

UI animations stay under 300ms. **Asymmetric timing:** Slow where user is deciding, fast where system responds.

---

### Component Patterns

#### Buttons — must feel responsive
```css
.button { transition: transform 160ms ease-out; }
.button:active { transform: scale(0.97); }
```
Scale 0.95–0.98. Applies to any pressable element.

#### Never animate from scale(0)
```css
/* Bad */  .entering { transform: scale(0); }
/* Good */ .entering { transform: scale(0.95); opacity: 0; }
```

#### Animate entry with @starting-style (modern CSS)
```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

#### Popovers — origin-aware
```css
/* Radix UI */ .popover { transform-origin: var(--radix-popover-content-transform-origin); }
/* Base UI  */ .popover { transform-origin: var(--transform-origin); }
```
Modals stay `transform-origin: center` — not anchored to a trigger.

#### Tooltips — skip delay on subsequent hovers
```css
.tooltip { transition: transform 125ms ease-out, opacity 125ms ease-out; }
.tooltip[data-instant] { transition-duration: 0ms; }
```

#### Blur crossfade trick
Add `filter: blur(2px)` during transition. Bridges visual gap. Keep under 20px (expensive in Safari).

#### CSS transitions over keyframes for interruptible UI
```css
/* Interruptible — good for dynamic UI */
.toast { transition: transform 400ms ease; }
/* Not interruptible — avoid for rapidly-triggered elements */
@keyframes slideIn { from { transform: translateY(100%); } to { transform: translateY(0); } }
```

#### Stagger animations
```css
.item { opacity: 0; transform: translateY(8px); animation: fadeIn 300ms ease-out forwards; }
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
@keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
```
Keep delays 30–80ms. Never block interaction during stagger.

---

### Spring Animations

Use springs when: drag interactions, elements that feel "alive", gestures interruptible mid-animation.

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }        // Apple approach — easier to reason
{ type: "spring", mass: 1, stiffness: 100, damping: 10 } // Traditional physics
```

Keep bounce subtle (0.1–0.3). **Interruptibility:** Springs maintain velocity when interrupted — CSS animations restart from zero.

---

### CSS Transform Mastery

```css
/* translateY percentages — relative to element's own size */
.drawer-hidden { transform: translateY(100%); }
.toast-enter   { transform: translateY(-100%); }

/* 3D transforms */
.wrapper { transform-style: preserve-3d; }
@keyframes orbit {
  from { transform: translate(-50%, -50%) rotateY(0deg) translateZ(72px) rotateY(360deg); }
  to   { transform: translate(-50%, -50%) rotateY(360deg) translateZ(72px) rotateY(0deg); }
}
```

---

### clip-path Animations

```css
/* inset shape */
.hidden  { clip-path: inset(0 100% 0 0); }  /* hidden from right */
.visible { clip-path: inset(0 0 0 0); }     /* fully visible */

/* Hold-to-delete pattern */
.overlay { clip-path: inset(0 100% 0 0); transition: clip-path 200ms ease-out; }
.button:active .overlay { clip-path: inset(0 0 0 0); transition: clip-path 2s linear; }
```

Image reveals on scroll: start `inset(0 0 100% 0)` → animate to `inset(0 0 0 0)` on viewport entry via IntersectionObserver.

---

### Gesture & Drag Interactions

```js
// Velocity-based dismissal
const velocity = Math.abs(swipeAmount) / timeTaken;
if (Math.abs(swipeAmount) >= SWIPE_THRESHOLD || velocity > 0.11) dismiss();

// Pointer capture for drag (continues even if pointer leaves element)
element.setPointerCapture(event.pointerId);
```

Allow upward drag with increasing friction — natural boundary, not a hard stop.

---

### Performance (Web)

- **Only animate `transform` and `opacity`** — runs on GPU, no layout/paint triggered
- Framer Motion GPU acceleration: use `{ transform: "translateX(100px)" }` not `{ x: 100 }`
- CSS animations beat JS under browser load — use CSS for predetermined, JS for dynamic/interruptible
- WAAPI for programmatic CSS performance:
```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

---

### Accessibility (Web)

```css
@media (prefers-reduced-motion: reduce) {
  /* Keep opacity/color. Remove movement and position animations. */
}
@media (hover: hover) and (pointer: fine) {
  .element:hover { transform: scale(1.05); } /* prevents hover triggering on touch tap */
}
```

```jsx
const shouldReduceMotion = useReducedMotion();
const closedX = shouldReduceMotion ? 0 : '-100%';
```

---

### Review Table

| Before | After | Why |
|---|---|---|
| `transition: all 300ms` | `transition: transform 200ms ease-out` | Never transition `all` |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing appears from nothing |
| `ease-in` on dropdown | `cubic-bezier(0.23, 1, 0.32, 1)` | ease-in feels sluggish |
| No `:active` on button | `transform: scale(0.97)` on `:active` | Buttons must feel responsive |
| `transform-origin: center` on popover | `var(--radix-popover-content-transform-origin)` | Scale from trigger |
| Duration 400ms on tooltip | 125–200ms | UI stays under 300ms |
| Same enter/exit speed | Exit faster than enter | Slow for deciding, fast for responding |
| Keyframes on toast | CSS transitions | Transitions retarget on interrupt |
| Framer `{ x: 100 }` under load | `{ transform: "translateX(100px)" }` | GPU acceleration |

---

## Mobile (RN)

React Native animation stack: **Reanimated 3** (primary), **Moti** (declarative), **react-native-gesture-handler v2** (gestures).

### Thread Model — Critical

Animations run on the **UI thread** (separate from JS thread). Understanding this prevents jank:
- `useAnimatedStyle` — runs on UI thread, never read JS state directly inside
- `runOnJS(fn)(value)` — cross back to JS thread for state updates
- Never put JS-only calls (`setState`, `console.log`) inside worklets — wrap in `runOnJS`

```jsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring, runOnJS } from 'react-native-reanimated';

const offset = useSharedValue(0);

const animatedStyle = useAnimatedStyle(() => ({
  transform: [{ translateX: offset.value }],
}));

function handleDismiss() {
  offset.value = withSpring(300, {}, (finished) => {
    if (finished) runOnJS(setVisible)(false); // JS state update after animation
  });
}
```

---

### Easing in Reanimated

Reanimated's `Easing` mirrors CSS curves:

```js
import { Easing } from 'react-native-reanimated';

// CSS equivalents
withTiming(value, { easing: Easing.out(Easing.cubic) })    // ease-out
withTiming(value, { easing: Easing.inOut(Easing.cubic) })  // ease-in-out
withTiming(value, { easing: Easing.bezier(0.23, 1, 0.32, 1) }) // custom cubic-bezier
```

---

### Timing Guidelines (RN)

Touch interactions feel slightly different than hover — add ~20–40ms for touch feedback:

| Element | Duration |
|---|---|
| Button press | 120–180ms |
| Bottom sheet / drawer | 300–500ms |
| Toast / snackbar | 250–400ms |
| Screen transition | 350–500ms |
| Scroll entry reveals | 500–700ms |

---

### Springs (Reanimated)

```jsx
withSpring(targetValue, {
  damping: 15,      // higher = less oscillation
  stiffness: 120,   // higher = faster
  mass: 1,
  overshootClamping: false,
  restDisplacementThreshold: 0.01,
  restSpeedThreshold: 0.01,
})

// Presets
withSpring(value, { damping: 20, stiffness: 90 })  // gentle iOS-like
withSpring(value, { damping: 10, stiffness: 100 }) // bouncy/playful
```

---

### Moti (Declarative API)

Moti wraps Reanimated with a prop-based API similar to Framer Motion:

```jsx
import { MotiView, MotiText } from 'moti';

<MotiView
  from={{ opacity: 0, translateY: 16 }}
  animate={{ opacity: 1, translateY: 0 }}
  exit={{ opacity: 0, translateY: -16 }}
  transition={{ type: 'spring', damping: 15, stiffness: 120 }}
/>

// Stagger with MotiView
import { AnimatePresence } from 'moti';
import { stagger } from 'moti/skeleton'; // or manual delay

{items.map((item, i) => (
  <MotiView
    key={item.id}
    from={{ opacity: 0, translateY: 8 }}
    animate={{ opacity: 1, translateY: 0 }}
    transition={{ delay: i * 60 }}
  />
))}
```

---

### Layout Animations (Entry/Exit)

```jsx
import Animated, { FadeIn, FadeOut, SlideInRight, Layout } from 'react-native-reanimated';

// Entry/exit animations on mount/unmount
<Animated.View entering={FadeIn.duration(300)} exiting={FadeOut.duration(200)}>
  {content}
</Animated.View>

// Smooth re-layout when items change
<Animated.View layout={Layout.springify()}>
  {items.map(...)}
</Animated.View>
```

---

### Gesture Handler

```jsx
import { GestureDetector, Gesture } from 'react-native-gesture-handler';

const panGesture = Gesture.Pan()
  .onUpdate((e) => {
    translateY.value = e.translationY;
  })
  .onEnd((e) => {
    const shouldDismiss = e.translationY > 100 || e.velocityY > 500;
    if (shouldDismiss) {
      translateY.value = withSpring(600);
      runOnJS(onDismiss)();
    } else {
      translateY.value = withSpring(0);
    }
  });

<GestureDetector gesture={panGesture}>
  <Animated.View style={animatedStyle}>
    {children}
  </Animated.View>
</GestureDetector>
```

---

### Reduced Motion (RN)

```jsx
import Animated, { useReducedMotion } from 'react-native-reanimated'; // Reanimated 3.6+

const prefersReducedMotion = useReducedMotion();

// Respect in animations
const animConfig = prefersReducedMotion
  ? { duration: 0 }
  : { type: 'spring', damping: 15, stiffness: 120 };
```

---

### Shared Element Transitions (Expo Router)

```jsx
import { SharedTransition } from 'react-native-reanimated';

// Source screen
<Animated.Image sharedTransitionTag="hero-image" source={...} />

// Destination screen
<Animated.Image sharedTransitionTag="hero-image" source={...} />
```

---

### Performance (RN)

- Only animate `transform` and `opacity` — same rule as web, triggers compositor, not layout
- Use `useSharedValue` + `useAnimatedStyle` — runs on UI thread, never drops frames
- `React.memo` around animated leaf components — prevent parent re-renders from killing animation
- Avoid `useState` for continuous animation values — always `useSharedValue`
- Test on a real device — Simulator doesn't represent true gesture feel or frame budget

---

### Haptic Feedback

Pair with animations for physical feel:
```jsx
import * as Haptics from 'expo-haptics';

// On press confirm
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

// On error
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

// On success
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
```
