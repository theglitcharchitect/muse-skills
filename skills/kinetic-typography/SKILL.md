---
name: kinetic-typography
description: "Variable font axis animation, split-text character reveals, text-as-hero-image patterns (clip-path with video/image fill), text stroke/outline, gradient text animation, scroll-driven text effects. The dominant 2026 visual trend."
tier: domain
triggers: "kinetic type, variable font, text animation, split text, text reveal, gradient text, text stroke, outlined text, text mask, hero typography, animated type"
version: "2.3.0"
metadata:
  pathPatterns:
    - "**/*.tsx"
    - "**/*.jsx"
---

## Layer 1: Decision Guidance

Kinetic typography is the single highest-impact visual technique in 2025-2026 design. When typography moves, it becomes the hero element -- no image, illustration, or 3D scene required. This skill covers variable font axis animation, split-text character reveals, text-as-hero-image patterns, text stroke/outline, gradient text animation, and scroll-driven text transforms. It replaces static display headings with living, responsive, story-telling type.

### When to Use

- **Hero sections** -- Text IS the visual. No hero image needed when type is at 15-25vw and animated.
- **Section reveals** -- Per-character or per-word entrance choreography draws the eye.
- **Scroll storytelling** -- Weight/width/slant morph as the user scrolls, reinforcing the narrative arc.
- **Brand statements** -- Outlined, gradient, or masked text communicates brand personality instantly.
- **Creative tension moments** -- Scale violence, weight snaps, or stroke flicker applied to type for controlled rule-breaking.
- **Loading/transition states** -- Variable font axis cycling creates elegant loading indicators.

### When NOT to Use

- **Body copy or long-form text** -- Use `typography` skill instead. Kinetic effects on body text destroy readability.
- **Data-dense layouts** -- Use `dashboard-patterns` or `chart-data-viz`. Moving text competes with data comprehension.
- **Accessibility-critical labels** -- Form labels, error messages, and navigation text must remain stable.
- **Below-the-fold content on slow connections** -- Heavy split-text JS on non-critical content wastes performance budget.

### Decision Tree

```
Is the text a display heading (h1/h2) or brand statement?
  YES -> Is a variable font loaded for this project?
    YES -> Is the effect scroll-linked?
      YES -> Variable font axis animation on scroll (Pattern 1 + Pattern 6)
      NO  -> Variable font hover/entrance animation (Pattern 1)
    NO -> Is the text the PRIMARY visual element (hero)?
      YES -> Text-as-hero-image with background-clip (Pattern 3)
      NO  -> Is outlined/hollow letterform the goal?
        YES -> Text stroke/outline (Pattern 4)
        NO  -> Gradient text animation (Pattern 5)
  NO -> Is this a reveal/entrance animation on short text?
    YES -> Split-text character reveal (Pattern 2)
    NO  -> Keep static. This skill does not apply.
```

### Pipeline Connection

- **Referenced by:** Creative Director during `/gen:discuss` for hero and section heading proposals
- **Referenced by:** Builder during `/gen:build` for section implementation
- **Consumed at:** `/gen:plan` workflow step 4 (section technique assignment)
- **Validated at:** `/gen:audit` under Creative Courage and Motion categories

---

## Layer 2: Award-Winning Examples

### Pattern 1: Variable Font Axis Animation

Animate `wght`, `wdth`, `slnt`, or custom axes on scroll or hover. Requires a variable font with declared axis ranges.

**Supported variable fonts and axes:**

| Font | wght | wdth | slnt | ital | opsz | Custom |
|------|------|------|------|------|------|--------|
| Recursive | 300-1000 | -- | -15-0 | 0-1 | -- | CASL 0-1, CRSV 0-1, MONO 0-1 |
| Inter Variable | 100-900 | 75-100 | -10-0 | -- | -- | -- |
| Clash Display Variable | 200-700 | -- | -- | -- | -- | -- |
| Instrument Serif Variable | 100-900 | -- | -- | -- | -- | -- |
| Space Grotesk Variable | 300-700 | -- | -- | -- | -- | -- |

```css
/* @font-face with axis ranges */
@font-face {
  font-family: 'Recursive';
  src: url('/fonts/Recursive-Variable.woff2') format('woff2-variations');
  font-weight: 300 1000;
  font-display: swap;
  font-style: oblique -15deg 0deg;
}
```

```tsx
// Variable font weight animation on scroll
import { useScroll, useTransform, motion } from 'motion/react';
import { useRef } from 'react';

export function KineticHeadline({ text }: { text: string }) {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });
  const fontWeight = useTransform(scrollYProgress, [0, 0.5], [300, 900]);
  const fontWidth = useTransform(scrollYProgress, [0, 0.5], [75, 100]);

  return (
    <motion.h1
      ref={ref}
      style={{
        fontVariationSettings: `'wght' ${fontWeight.get()}, 'wdth' ${fontWidth.get()}`,
      }}
      className="font-display text-[clamp(3rem,8vw,8rem)] leading-[0.9] text-text"
    >
      {text}
    </motion.h1>
  );
}
```

```tsx
// Variable font hover with spring physics
import { motion, useMotionValue, useSpring } from 'motion/react';

export function HoverWeightHeadline({ text }: { text: string }) {
  const weight = useMotionValue(400);
  const smoothWeight = useSpring(weight, { stiffness: 300, damping: 20 });

  return (
    <motion.h1
      onHoverStart={() => weight.set(900)}
      onHoverEnd={() => weight.set(400)}
      style={{ fontVariationSettings: `'wght' ${smoothWeight.get()}` }}
      className="font-display text-[clamp(2.5rem,6vw,6rem)] leading-[0.95] cursor-default text-text"
    >
      {text}
    </motion.h1>
  );
}
```

### Pattern 2: Split-Text Character Reveal

Per-character or per-word scroll animation. Handles SSR, cleanup, and accessible fallback.

```tsx
// Split-text character reveal with stagger
'use client';

import { useRef, useMemo } from 'react';
import { motion, useInView } from 'motion/react';

interface SplitTextProps {
  text: string;
  as?: 'h1' | 'h2' | 'h3' | 'p';
  className?: string;
  staggerDelay?: number;
  splitBy?: 'char' | 'word';
}

export function SplitTextReveal({
  text,
  as: Tag = 'h1',
  className = '',
  staggerDelay = 0.03,
  splitBy = 'char',
}: SplitTextProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-10%' });

  const units = useMemo(() => {
    if (splitBy === 'word') return text.split(' ');
    return text.split('');
  }, [text, splitBy]);

  return (
    <Tag ref={ref} className={`overflow-hidden ${className}`} aria-label={text}>
      {units.map((unit, i) => (
        <motion.span
          key={`${unit}-${i}`}
          aria-hidden="true"
          initial={{ y: '110%', opacity: 0 }}
          animate={isInView ? { y: '0%', opacity: 1 } : undefined}
          transition={{
            duration: 0.5,
            ease: [0.16, 1, 0.3, 1],
            delay: i * staggerDelay,
          }}
          className="inline-block"
          style={{ willChange: 'transform' }}
        >
          {unit === ' ' ? '\u00A0' : unit}
        </motion.span>
      ))}
    </Tag>
  );
}
```

**Stagger timing by archetype:**

| Archetype | staggerDelay | Duration | Easing | Notes |
|-----------|-------------|----------|--------|-------|
| Brutalist | 0 (instant) | 0 | steps(1) | All chars appear at once or in hard grid blocks |
| Ethereal | 0.06 | 0.8 | ease-out | Slow, dreamlike word-by-word |
| Kinetic | 0.02 | 0.4 | spring(300,20) | Bouncy overshoot per character |
| Japanese Minimal | 0.12 | 1.0 | ease-in-out | One character at a time, extreme restraint |
| Neon Noir | 0.04 | 0.3 | linear | Rapid flicker, glow on each arrival |
| Editorial | 0.03 | 0.5 | cubic-bezier(0.16,1,0.3,1) | Refined, no bounce |

### Pattern 3: Text-as-Hero-Image

Display text at 15-25vw so it IS the visual content. No hero image needed.

```tsx
// Gradient-filled text
export function GradientHeroText({ text }: { text: string }) {
  return (
    <h1
      className="text-[clamp(4rem,18vw,20rem)] font-display font-bold leading-[0.85]
                 bg-gradient-to-br from-primary via-accent to-secondary
                 bg-clip-text text-transparent"
    >
      {text}
    </h1>
  );
}
```

```tsx
// Video-filled text
export function VideoHeroText({ text, videoSrc }: { text: string; videoSrc: string }) {
  return (
    <div className="relative w-full h-screen flex items-center justify-center overflow-hidden">
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 w-full h-full object-cover"
        aria-hidden="true"
      >
        <source src={videoSrc} type="video/mp4" />
      </video>
      <h1
        className="relative text-[clamp(4rem,20vw,22rem)] font-display font-black leading-[0.85]
                   mix-blend-screen text-white select-none"
        /* For true clip: use SVG clipPath or the CSS approach below */
      >
        {text}
      </h1>
    </div>
  );
}
```

```css
/* CSS background-clip: text with image fill */
.hero-text-image-fill {
  font-size: clamp(4rem, 18vw, 20rem);
  font-weight: 900;
  line-height: 0.85;
  background-image: url('/hero-texture.jpg');
  background-size: cover;
  background-position: center;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent; /* fallback */
}
```

```css
/* mix-blend-mode text knockout */
.hero-text-knockout {
  font-size: clamp(4rem, 20vw, 22rem);
  font-weight: 900;
  color: white;
  mix-blend-mode: screen; /* or multiply, difference */
  position: relative;
  z-index: 1;
}
```

### Pattern 4: Text Stroke / Outline

Hollow letterforms using `-webkit-text-stroke`. Fill-on-hover animation per archetype.

```tsx
// Outlined text with hover fill
'use client';

import { motion } from 'motion/react';

interface OutlinedTextProps {
  text: string;
  strokeWidth?: string;
  strokeColor?: string;
  fillColor?: string;
}

export function OutlinedText({
  text,
  strokeWidth = '2px',
  strokeColor = 'var(--color-text)',
  fillColor = 'var(--color-primary)',
}: OutlinedTextProps) {
  return (
    <motion.h2
      className="text-[clamp(3rem,10vw,10rem)] font-display font-bold leading-[0.9] cursor-default"
      style={{
        WebkitTextStroke: `${strokeWidth} ${strokeColor}`,
        WebkitTextFillColor: 'transparent',
      }}
      whileHover={{
        WebkitTextFillColor: fillColor,
        transition: { duration: 0.4, ease: 'easeOut' },
      }}
    >
      {text}
    </motion.h2>
  );
}
```

**Stroke weights by archetype:**

| Archetype | Stroke Width | Fill Behavior | Notes |
|-----------|-------------|---------------|-------|
| Brutalist | 3-4px | Instant fill (steps(1)) | Raw, heavy outlines |
| Ethereal | 0.5-1px | Slow fade fill (800ms) | Barely-there hairline |
| Kinetic | 2px | Spring fill with overshoot | Color overshoots then settles |
| Neo-Corporate | 1-2px | Clean ease-out (300ms) | Professional, no spring |
| Neon Noir | 1px | Glow pulse before fill | text-shadow glow first, then fill |

```css
/* Fallback for browsers without -webkit-text-stroke */
@supports not (-webkit-text-stroke: 1px black) {
  .outlined-text {
    color: transparent;
    text-shadow:
      -1px -1px 0 var(--color-text),
       1px -1px 0 var(--color-text),
      -1px  1px 0 var(--color-text),
       1px  1px 0 var(--color-text);
  }
}
```

### Pattern 5: Gradient Text Animation

Animated gradient behind clipped text. DNA-token-driven color stops.

```tsx
// Animated gradient text with CSS
export function AnimatedGradientText({
  text,
  className = '',
}: {
  text: string;
  className?: string;
}) {
  return (
    <h2
      className={`text-[clamp(2rem,6vw,6rem)] font-display font-bold leading-tight
                   bg-clip-text text-transparent animate-gradient-shift ${className}`}
      style={{
        backgroundImage: `linear-gradient(
          90deg,
          var(--color-primary),
          var(--color-accent),
          var(--color-secondary),
          var(--color-primary)
        )`,
        backgroundSize: '300% 100%',
      }}
    >
      {text}
    </h2>
  );
}
```

```css
/* Tailwind v4 @theme extension for gradient animation */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient-shift {
  animation: gradient-shift 6s ease infinite;
}
```

```tsx
// Temperature-shifting gradient (warm to cool)
export function TemperatureGradientText({ text }: { text: string }) {
  return (
    <h2
      className="text-[clamp(2rem,6vw,6rem)] font-display font-bold
                 bg-clip-text text-transparent animate-temperature-shift"
      style={{
        backgroundImage: `linear-gradient(
          90deg,
          var(--color-glow),
          var(--color-highlight),
          var(--color-accent),
          var(--color-signature)
        )`,
        backgroundSize: '400% 100%',
      }}
    >
      {text}
    </h2>
  );
}
```

### Pattern 6: Scroll-Driven Text Transforms

Text that scales, rotates, translates, or changes weight as the user scrolls. CSS scroll-driven first, Motion fallback.

```css
/* CSS scroll-driven animation (modern browsers) */
@supports (animation-timeline: view()) {
  .scroll-scale-text {
    animation: scaleOnScroll linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 50%;
  }

  @keyframes scaleOnScroll {
    from {
      transform: scale(0.5);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }
}
```

```tsx
// Motion fallback for browsers without scroll-driven animations
import { useScroll, useTransform, motion } from 'motion/react';
import { useRef } from 'react';

export function ScrollScaleHeadline({ text }: { text: string }) {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'center center'],
  });
  const scale = useTransform(scrollYProgress, [0, 1], [0.5, 1]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [0, 1]);

  return (
    <motion.h2
      ref={ref}
      style={{ scale, opacity }}
      className="font-display text-[clamp(3rem,10vw,10rem)] leading-[0.9] text-text origin-center"
    >
      {text}
    </motion.h2>
  );
}
```

```tsx
// Scroll-linked rotation + weight shift
import { useScroll, useTransform, motion } from 'motion/react';
import { useRef } from 'react';

export function ScrollRotateWeightText({ text }: { text: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });
  const rotate = useTransform(scrollYProgress, [0, 1], [-5, 5]);
  const weight = useTransform(scrollYProgress, [0, 1], [300, 900]);

  return (
    <div ref={ref} className="py-[20vh]">
      <motion.h2
        style={{
          rotate,
          fontVariationSettings: `'wght' ${weight.get()}`,
        }}
        className="font-display text-[clamp(3rem,8vw,8rem)] leading-[0.9] text-text text-center"
      >
        {text}
      </motion.h2>
    </div>
  );
}
```

### Pattern 7: Text Balance and Wrapping

CSS native text wrapping for display headings. Eliminates orphans and awkward line breaks.

```css
/* Use text-wrap: balance for headings (equal-width lines) */
h1, h2, h3 {
  text-wrap: balance;
}

/* Use text-wrap: pretty for body text (prevents orphans on last line) */
p {
  text-wrap: pretty;
}
```

**When to use each:**

| Property | Use Case | Browser Support | Fallback |
|----------|----------|----------------|----------|
| `text-wrap: balance` | Headings, short text blocks (< 6 lines) | Chrome 114+, Firefox 121+ | No fallback needed -- degrades gracefully |
| `text-wrap: pretty` | Paragraphs, longer text | Chrome 117+, Firefox 121+ | No fallback needed -- degrades to normal wrapping |

### Per-Archetype Kinetic Typography Examples

#### Brutalist

Hard weight snaps, monospace character reveals, no curves, no easing.

```tsx
// Brutalist: Instant weight snap on scroll thresholds
import { useScroll, useTransform, motion } from 'motion/react';

export function BrutalistSnap({ text }: { text: string }) {
  const { scrollYProgress } = useScroll();
  const weight = useTransform(
    scrollYProgress,
    [0, 0.25, 0.5, 0.75],
    [100, 900, 100, 900] // hard steps, no interpolation
  );

  return (
    <motion.h1
      style={{ fontVariationSettings: `'wght' ${weight.get()}` }}
      className="font-mono text-[clamp(3rem,10vw,10rem)] leading-none uppercase text-text"
    >
      {text}
    </motion.h1>
  );
}
```

#### Ethereal

Slow weight drifts, word-by-word fade, translucent overlapping layers.

```tsx
// Ethereal: Layered translucent text with slow weight drift
export function EtherealLayers({ text }: { text: string }) {
  return (
    <div className="relative h-[50vh] flex items-center justify-center">
      {[0.15, 0.3, 1].map((opacity, i) => (
        <h1
          key={i}
          className="absolute font-display text-[clamp(4rem,15vw,16rem)] leading-[0.85] text-text"
          style={{
            opacity,
            transform: `translateY(${i * -8}px)`,
            fontVariationSettings: `'wght' ${300 + i * 200}`,
            transition: 'font-variation-settings 2s ease-out',
          }}
        >
          {text}
        </h1>
      ))}
    </div>
  );
}
```

#### Kinetic

Spring-based character bounces, overshoot on weight change.

```tsx
// Kinetic: Spring character bounce entrance
import { motion } from 'motion/react';

export function KineticBounce({ text }: { text: string }) {
  return (
    <h1 className="font-display text-[clamp(3rem,10vw,10rem)] leading-none text-text" aria-label={text}>
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          aria-hidden="true"
          initial={{ y: -80, opacity: 0, scale: 1.4 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          transition={{
            type: 'spring',
            stiffness: 300,
            damping: 15,
            delay: i * 0.02,
          }}
          className="inline-block"
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </h1>
  );
}
```

#### Japanese Minimal

Single character reveals with long delays, extreme restraint.

```tsx
// Japanese Minimal: One character at a time, long pauses
import { motion, useInView } from 'motion/react';
import { useRef } from 'react';

export function JapMinimalReveal({ text }: { text: string }) {
  const ref = useRef<HTMLHeadingElement>(null);
  const isInView = useInView(ref, { once: true });

  return (
    <h1 ref={ref} className="font-display text-[clamp(3rem,12vw,12rem)] leading-[0.9] text-text tracking-[0.1em]" aria-label={text}>
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          aria-hidden="true"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : undefined}
          transition={{ duration: 1.0, delay: i * 0.12, ease: 'easeInOut' }}
          className="inline-block"
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </h1>
  );
}
```

#### Neon Noir

Glow-pulse on individual characters, flickering text-stroke.

```tsx
// Neon Noir: Glow pulse with flicker
import { motion } from 'motion/react';

export function NeonFlickerText({ text }: { text: string }) {
  return (
    <h1 className="font-display text-[clamp(3rem,10vw,10rem)] leading-none text-transparent" aria-label={text}>
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          aria-hidden="true"
          className="inline-block"
          style={{
            WebkitTextStroke: '1px var(--color-glow)',
            textShadow: `0 0 10px var(--color-glow), 0 0 40px var(--color-glow)`,
          }}
          animate={{
            opacity: [1, 0.4, 1, 0.7, 1],
            textShadow: [
              '0 0 10px var(--color-glow), 0 0 40px var(--color-glow)',
              '0 0 2px var(--color-glow), 0 0 8px var(--color-glow)',
              '0 0 10px var(--color-glow), 0 0 40px var(--color-glow)',
            ],
          }}
          transition={{
            duration: 2 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.04,
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </h1>
  );
}
```

### Reduced Motion Handling

All kinetic typography patterns MUST respect `prefers-reduced-motion`. Provide a static fallback.

```tsx
// Hook for reduced motion detection
import { useReducedMotion } from 'motion/react';

export function AccessibleKineticText({ text }: { text: string }) {
  const prefersReduced = useReducedMotion();

  if (prefersReduced) {
    return (
      <h1 className="font-display text-[clamp(3rem,8vw,8rem)] leading-[0.9] text-text">
        {text}
      </h1>
    );
  }

  return <SplitTextReveal text={text} />;
}
```

```css
/* CSS fallback for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .animate-gradient-shift,
  .scroll-scale-text {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
```

### Reference Sites

- **Locomotive.ca** -- Variable font weight morphing on scroll with full-viewport type. Masterclass in text-as-hero-image without any imagery.
- **Haus.gg** -- Split-text character reveals with per-archetype stagger timing. Uses Clash Display Variable with weight animation on hover.
- **Resn.co.nz** -- Extreme kinetic type with 3D transforms, scroll-driven rotation, and outlined text that fills on intersection.
- **Lusion.co** -- Text-stroke with glow effects, video-filled letterforms, and scroll-linked scale transforms.
- **Obys.agency** -- Japanese-minimal-inspired single-character reveals, extreme restraint, and translucent layered type.

---

## Layer 3: Integration Context

### DNA Connection

| DNA Token | Usage in This Skill |
|-----------|-------------------|
| `--font-display` | All kinetic text uses the project display font. Variable font must be loaded as the display font. |
| `--font-body` | Never animated. Body font stays static for readability. |
| `--motion-duration` | Base duration for character stagger and weight transitions. |
| `--motion-ease` | Default easing curve for text reveals and gradient shifts. |
| `--motion-spring-stiffness` | Spring stiffness for Kinetic archetype bounces and overshoot. |
| `--motion-spring-damping` | Spring damping for settling behavior. |
| `--color-primary` | First gradient stop in gradient text patterns. |
| `--color-accent` | Mid gradient stop and text-stroke color. |
| `--color-secondary` | End gradient stop in gradient text patterns. |
| `--color-glow` | Neon Noir glow pulse color, text-shadow value. |
| `--color-signature` | Expressive gradient stop for temperature shifts. |

### Archetype Variants

| Archetype | Technique Preference | Forbidden |
|-----------|---------------------|-----------|
| Brutalist | Weight snaps (steps), monospace reveals, raw outlines | Smooth gradients, spring easing, translucent layers |
| Ethereal | Slow weight drift, word fade, translucent overlapping | Hard snaps, monospace, thick strokes |
| Kinetic | Spring bounces, overshoot weight, fast stagger | Static text, slow reveals, restraint |
| Japanese Minimal | Single char reveal, extreme delay, opacity only | Bouncing, gradients, video fill, glow |
| Neon Noir | Glow pulse, flicker, thin stroke, dark bg required | Warm colors, balance-only, no glow |
| Editorial | Refined stagger, weight on scroll, no bounce | Spring physics, glow, video fill |
| Neo-Corporate | Clean weight transitions, outlined headings | Flicker, glitch, extreme sizes |
| Luxury/Fashion | Hairline strokes, slow gradient, restrained reveals | Thick strokes, fast animations, bounce |
| Retro-Future | Scanline overlay on text, CRT flicker, mono font | Organic curves, warm gradients |

### Pipeline Stage

- **Input from:** Design DNA (font family, color tokens, motion tokens), Archetype selection (technique constraints)
- **Output to:** Builder sections (hero, section headings), Quality Gate (motion + creative courage scores)

### Related Skills

- `cinematic-motion` -- Kinetic typography is a subset of motion design. This skill provides typography-specific patterns; cinematic-motion provides the broader motion system.
- `design-dna` -- DNA tokens drive font choice, color stops, and motion timing for all kinetic text.
- `design-archetypes` -- Each archetype constrains which kinetic techniques are permitted or forbidden.
- `emotional-arc` -- Beat type determines motion intensity: Hook/Peak beats get heavy kinetic type, Breathe beats get none.
- `performance-animation` -- Variable font files are large. Coordinate with performance skill for font subsetting and loading strategies.
- `typography` -- Static typography rules (scale, measure, vertical rhythm) still apply to kinetic text. This skill extends but does not replace typography fundamentals.
- `responsive-design` -- Font sizes use `clamp()` and viewport units. Kinetic effects may need to be reduced or simplified on mobile breakpoints.
- `wow-moments` -- Kinetic typography is a prime candidate for signature "wow" moments at Hook and Peak beats.

---

## Layer 4: Anti-Patterns

### Anti-Pattern: Non-Variable Font Axis Animation

**What goes wrong:** Animating `font-weight` on a font that only has static weight files (e.g., Inter 400 and 700 as separate files) causes ugly weight snapping instead of smooth interpolation. The browser jumps between the two nearest static weights.
**Instead:** Verify the font is a true variable font file (`woff2-variations` format) with a continuous axis range. Load it with `@font-face` declaring `font-weight: 300 1000` (the full range). If no variable font is available, use `transform: scale()` or `opacity` animation instead of weight animation.

### Anti-Pattern: Split Text Without SSR Handling

**What goes wrong:** Using DOM-based text splitting libraries (SplitType, splitting.js) in SSR frameworks (Next.js, Astro) causes hydration mismatch. The server renders the text as a single node; the client splits it into spans, causing a flash of unstyled content and CLS (Cumulative Layout Shift).
**Instead:** Split text in React with `useMemo` on the string (as shown in Pattern 2). The split happens identically on server and client. Wrap each character in `<span>` during render, not via DOM manipulation. Add `aria-label` on the parent and `aria-hidden` on each span.

### Anti-Pattern: Text-Stroke Without Browser Fallback

**What goes wrong:** `-webkit-text-stroke` is a non-standard property. While widely supported, it renders differently across browsers -- Firefox may show thicker strokes, and older Safari versions clip incorrectly. Relying on it without fallback creates inconsistent designs.
**Instead:** Always include an `@supports not (-webkit-text-stroke: 1px black)` fallback using `text-shadow` to simulate outlines (as shown in Pattern 4). Test on Firefox and Safari.

### Anti-Pattern: Gradient Text With Insufficient Contrast

**What goes wrong:** `background-clip: text` with a gradient makes parts of the text low-contrast as the gradient passes through light colors against a light background (or dark on dark). This fails WCAG 2.1 AA (4.5:1 ratio for normal text, 3:1 for large text).
**Instead:** Ensure ALL gradient color stops maintain at least 3:1 contrast against the background (kinetic text is always large/display). Use DNA color tokens that are pre-validated for contrast. Test with the darkest and lightest points of the gradient independently.

### Anti-Pattern: Unrestricted Kinetic Text on Mobile

**What goes wrong:** Complex per-character animations with springs, variable font axis cycling, and scroll-driven transforms cause jank on mobile devices. Variable font files (often 200KB+) block first paint.
**Instead:** Reduce split-text to word-level on mobile (fewer DOM nodes). Simplify spring physics to CSS transitions. Subset variable fonts to only the axes used. Use `font-display: swap` and preload the font file. Consider disabling scroll-driven weight animation below 768px.

---

## Machine-Readable Constraints

| Parameter | Min | Max | Unit | Enforcement |
|-----------|-----|-----|------|-------------|
| Display font size (hero) | 15 | 25 | vw | SOFT -- warn if outside range |
| Display font size (section heading) | 3 | 12 | rem (clamp) | SOFT -- warn if outside range |
| Character stagger delay | 0.01 | 0.15 | s | HARD -- reject if outside range |
| Gradient animation duration | 3 | 12 | s | SOFT -- warn if outside range |
| Variable font file size | 0 | 300 | KB | SOFT -- warn if over budget |
| Text-stroke width | 0.5 | 4 | px | SOFT -- warn if outside range |
| Max kinetic headings per page | 1 | 4 | count | HARD -- reject if more than 4 |
| WCAG contrast ratio (large text) | 3 | -- | :1 | HARD -- reject if below 3:1 |
| Split-text max characters | 1 | 80 | chars | SOFT -- warn if over 80 for performance |

---

## v3.2 Addendum: GSAP 3.13 Fully Free

Major context shift: since Webflow acquisition (May 2024), GSAP ships fully free — **SplitText, ScrollSmoother, MorphSVG, DrawSVG, all former Club plugins** are default install. Remove any "paid plugin" caveats from pre-v3.2 guidance.

### SplitText 3.13 — rewrite highlights

```ts
import { SplitText } from 'gsap/SplitText';  // FREE since 3.13

const split = SplitText.create('.headline', {
  type: 'chars, words, lines',
  mask: 'lines',      // NEW: built-in overflow mask, no CSS hack needed
  autoSplit: true,    // NEW: re-splits on font-load + ResizeObserver (200ms debounce)
  onSplit: self => {
    gsap.from(self.chars, { y: 100, opacity: 0, stagger: 0.02, duration: 0.8, ease: 'power4.out' });
  },
});
```

- `autoSplit: true` → fixes FOUT-causes-jumpy-text bug. Listens to `document.fonts.loadingdone` and ResizeObserver.
- `mask: 'lines'` → replaces manual `overflow: hidden` + inline-block wrapper pattern.
- `onSplit` callback fires initial split AND each auto-re-split — re-trigger animations here.

### Variable-font morphing (2026 Awwwards staple)

```ts
gsap.to(split.chars, {
  fontVariationSettings: '"wght" 900, "slnt" -15',
  duration: 2,
  stagger: { each: 0.05, from: 'random', repeat: -1, yoyo: true },
  ease: 'sine.inOut',
});
```

Variable fonts with good axis coverage: Recursive (wght + slnt + MONO + CASL), Inter (wght + ital), Roboto Flex, Bricolage Grotesque.

### ScrollSmoother now free

```ts
ScrollSmoother.create({
  wrapper: '#smooth-wrapper',
  content: '#smooth-content',
  smooth: 1.5,
  effects: true,           // enables [data-speed] + [data-lag] on children
  normalizeScroll: true,
});
```

Competitive alternative to Lenis in 2026 with tighter ScrollTrigger integration.

### Splitting.js vs SplitText — updated recommendation

SplitText 3.13 is strictly superior. Use Splitting.js only for non-GSAP projects.

### Remove from earlier skill guidance

Delete any "Club GreenSock required" / "SplitText is paid" language in earlier 4 layers. Those caveats are obsolete.

