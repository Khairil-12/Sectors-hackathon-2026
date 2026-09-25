# DESIGN.md — IDX Copilot Design System

> **Source of truth** for all visual and interface decisions in the **AI IDX Investment Research Copilot**.
> Every modification to templates in `templates/*` and `src/research/templates/*` must reference and conform to this document.
> Do not write one-off arbitrary styles at the template call site — use the tokens and component patterns defined here.

---

## Reference Design

The **IDX Copilot** interface is designed as an institutional-grade investment research terminal inspired by modern financial intelligence platforms:
a focused, high-density two-zone layout featuring a **deep dark sidebar** (`--sidebar`) and a **rich dark research canvas** (`--background`),
accented with **lime green** (`oklch(0.88 0.17 132)`) as the primary interactive and high-conviction signal color.

**Key adaptation:** Dark mode is the **primary and default** visual environment for IDX Copilot. Equity analysts, portfolio managers, and retail investors require low-glare, high-contrast visual environments during extended market sessions. All component styling targets dark mode first.

---

## 1. Design Principles

**1. Dark by default.** Financial research requires prolonged focus over dense data sets. The application ships in dark mode out of the box with deliberate contrast between the canvas (`--background`) and elevated surfaces (`--card`).

**2. Lime green is the only accent.** All primary interactive elements, active navigation states, "Analyze" generation triggers, and high-conviction positive highlights use `--primary` (lime green). Restricting the primary accent ensures the research interface remains cohesive, disciplined, and instantly recognizable.

**3. Financial signals have semantic colors.** Market data carries universally understood financial implications: red for capital outflow, price decline, and bearish risk; orange for valuation premium warning, distribution divergence, and high leverage; green for capital accumulation, undervalued status, and bullish drivers. These strictly map to `--destructive`, `--warning`, and `--primary` (or chart series), never arbitrary colors.

**4. Rounded, not sharp.** `--radius` is `1rem` (16px). All analytical cards, prompt containers, action buttons, and ticker pills use the standardized radius scale. The interface feels approachable and modern without aggressive brutalist edges.

**5. Hierarchy through opacity, not new colors.** Secondary metrics, ticker labels, citation metadata, and footnotes use `--muted-foreground` (`oklch(0.65 0.01 265)`), not arbitrary greys. Subtle containers use `--muted`. The chromatic palette remains minimal, letting financial data take precedence.

---

## 2. Color System

### 2.1 CSS Variables Reference

All semantic variables are declared in `src/app.css` (or `static/src/input.css`) inside `@layer base` or `@theme`.

#### Core Semantic Variables

| Variable | Dark Mode Value | Light Mode Value | Semantic Role in IDX Copilot |
|---|---|---|---|
| `--background` | `oklch(0.15 0.01 265)` | `oklch(0.98 0.005 265)` | Main workspace canvas background |
| `--foreground` | `oklch(0.95 0.01 265)` | `oklch(0.25 0.02 265)` | Primary typography, headers, metric values |
| `--card` | `oklch(0.20 0.01 265)` | `oklch(1 0 0)` | Research cards, metric panels, prompt composer |
| `--card-foreground` | `oklch(0.95 0.01 265)` | `oklch(0.25 0.02 265)` | Text and metrics on card surfaces |
| `--popover` | `oklch(0.20 0.01 265)` | `oklch(1 0 0)` | Autocomplete ticker dropdown, filter popovers |
| `--popover-foreground` | `oklch(0.95 0.01 265)` | `oklch(0.25 0.02 265)` | Text inside dropdowns and popovers |
| `--primary` | `oklch(0.88 0.17 132)` | `oklch(0.88 0.17 132)` | Lime green accent — Analyze CTA, active filters, bullish signals |
| `--primary-foreground` | `oklch(0.20 0.01 265)` | `oklch(0.20 0.01 265)` | Text on lime green buttons and badges |
| `--secondary` | `oklch(0.25 0.01 265)` | `oklch(0.95 0.01 265)` | Secondary action surfaces, prompt template chips |
| `--secondary-foreground` | `oklch(0.95 0.01 265)` | `oklch(0.25 0.02 265)` | Text on secondary surfaces |
| `--muted` | `oklch(0.22 0.01 265)` | `oklch(0.95 0.01 265)` | Subtle container backgrounds, code chips, citation boxes |
| `--muted-foreground` | `oklch(0.65 0.01 265)` | `oklch(0.65 0.01 265)` | Metric labels, subheaders, citations, timestamps |
| `--accent` | `oklch(0.88 0.17 132)` | `oklch(0.88 0.17 132)` | Interactive highlight states, matching primary |
| `--accent-foreground` | `oklch(0.20 0.01 265)` | `oklch(0.20 0.01 265)` | Text on accent backgrounds |
| `--destructive` | `oklch(0.64 0.208 25.3)` | `oklch(0.64 0.208 25.3)` | Bearish risks, net foreign outflows, report deletion |
| `--warning` | `oklch(0.77 0.165 70.1)` | `oklch(0.77 0.165 70.1)` | Flow divergence alerts, valuation caution, prompt out-of-scope |
| `--border` | `oklch(0.28 0.01 265)` | `oklch(0.90 0.01 265)` | Card borders, table dividers, input boundaries |
| `--input` | `oklch(0.28 0.01 265)` | `oklch(0.90 0.01 265)` | Search fields, textarea borders |
| `--ring` | `oklch(0.88 0.17 132)` | `oklch(0.88 0.17 132)` | Focus rings on prompt inputs and buttons |

#### Sidebar Variables

The navigation sidebar is **always dark**, establishing persistent architectural structure.

| Variable | Value | Usage in Navigation |
|---|---|---|
| `--sidebar` | `oklch(0.18 0.01 265)` | Sidebar background canvas |
| `--sidebar-foreground` | `oklch(0.95 0.01 265)` | Navigation labels and icons |
| `--sidebar-primary` | `oklch(0.88 0.17 132)` | Active navigation item background pill |
| `--sidebar-primary-foreground` | `oklch(0.20 0.01 265)` | Text on active navigation item |
| `--sidebar-accent` | `oklch(0.22 0.01 265)` | Nav item hover background state |
| `--sidebar-accent-foreground` | `oklch(1 0 0)` | Text on hovered nav item |
| `--sidebar-border` | `oklch(0.28 0.01 265)` | Sidebar internal dividers and right border |
| `--sidebar-ring` | `oklch(0.88 0.17 132)` | Focus ring within sidebar elements |

#### Dark Variant Variables

Pre-calculated deeper tones for hover and pressed states.

| Variable | Usage in IDX Copilot |
|---|---|
| `--primary-dark` | Hover state on "Analyze" and primary action buttons |
| `--accent-dark` | Hover state on ticker chips and interactive pills |
| `--destructive-dark` | Hover state on "Delete Report" or "Remove from Watchlist" buttons |
| `--warning-dark` | Hover state on warning callouts and alert dismissals |
| `--muted-dark` | Hover state on secondary template prompt chips |

#### Chart Variables

Standard series colors for equity visualization, foreign flow histograms, and multi-stock comparisons.

| Variable | Value | Semantic Financial Role |
|---|---|---|
| `--chart-1` | `oklch(0.88 0.17 132)` | Primary stock / Net institutional foreign inflow (Lime) |
| `--chart-2` | `oklch(0.72 0.192 149.6)` | Secondary comparison peer / Sector average |
| `--chart-3` | `oklch(0.62 0.188 259.8)` | Tertiary benchmark index (IHSG / LQ45) |
| `--chart-4` | `oklch(0.77 0.165 70.1)` | Moderate flow / Valuation caution / Neutral volume (Amber) |
| `--chart-5` | `oklch(0.64 0.208 25.3)` | Net foreign outflow / Downward price momentum (Red) |

---

### 2.2 IDX Copilot Semantic Tokens

These tokens govern how financial domain concepts map to the standardized CSS color variables. Never use arbitrary hex colors.

#### Market Sentiment & Foreign Flow Signals

| Domain Concept | Visual Signal | CSS Variable | Visual Token |
|---|---|---|---|
| Net Institutional Inflow | Positive institutional buying (> 0 IDR) | `--primary` | Lime green bar / text |
| Net Institutional Outflow | Institutional distribution (< 0 IDR) | `--destructive` | Red bar / text |
| Accumulation Divergence | Price drops while foreign flow surges | `--primary` + `--warning` border | Lime badge with amber alert |
| Distribution Warning | Price surges while foreign flow dumps | `--destructive` + `--warning` border | Red badge with amber alert |
| Neutral / Inactive Flow | Consolidation / Balanced volume | `--muted-foreground` | Slate grey badge |

#### Fundamental Valuation Verdicts

| Verdict | Variable | Visual Appearance | Meaning |
|---|---|---|---|
| **Undervalued** | `--primary` | Lime green pill | Trading at attractive discount to peers / intrinsic value |
| **Fair Value** | `--warning` | Amber pill | Trading within normal historical standard deviation |
| **Overvalued** | `--destructive` | Red pill | Trading at extended multiples relative to fundamentals |

#### Analysis & Copilot Agent Status

| Status | Variable | Component Pattern |
|---|---|---|
| **Synthesizing / Streaming** | `--primary` | Animated pulsing dot, spinner, elapsed timer |
| **Completed Report** | `--primary` | Solid lime badge + execution latency tag |
| **Out of Scope Query** | `--warning` | Amber warning callout with financial suggestions |
| **Upstream Error / 503** | `--destructive` | Red alert callout with retry button |

#### Ticker & Category Badges

| Entity Type | Variable | Visual Pattern |
|---|---|---|
| IDX Equity Ticker (e.g., `BBCA`) | `--card` + `--primary` | Monospace pill with green dot indicator |
| Index / Macro Benchmark (`IHSG`) | `--muted` + `--muted-foreground` | Subtle grey chip |
| Watchlist Active Item | `--primary` | Star icon filled with lime accent |
| Verified Citation | `--muted` + `--primary` hover | Accordion link with endpoint label |

---

## 3. Typography

IDX Copilot uses a high-performance system font stack. Financial dashboards open for extended hours require zero font download latency and crystal-clear tabular alignment.

```css
--font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
             Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-mono: ui-monospace, 'Cascadia Code', 'Fira Code', 'Roboto Mono', monospace;
```

### Type Scale

| Name | Size | Weight | Line Height | IDX Copilot Usage |
|---|---|---|---|---|
| `text-2xl` | 24px | 700 | 1.2 | Report titles, company names, key financial totals |
| `text-xl` | 20px | 600 | 1.3 | Section headers ("Fundamental Analysis", "Foreign Flow & Momentum") |
| `text-lg` | 18px | 600 | 1.4 | Card titles, metric header values, modal titles |
| `text-base` | 16px | 400 | 1.5 | Executive summary narratives, investment thesis copy |
| `text-sm` | 14px | 400 / 500 | 1.5 | Metric labels (P/E, P/B, ROE), table row text, input text |
| `text-xs` | 12px | 400 / 600 | 1.4 | Badges, ticker pills, data source citations, table headers |
| `text-2xs` | 11px | 500 | 1.3 | Timestamps, exchange disclaimer, keyboard shortcuts (`Ctrl+Enter`) |

### Text Color Usage

| Context | Variable |
|---|---|
| Primary report copy & titles | `--foreground` |
| Secondary metric labels & subtitles | `--muted-foreground` |
| Disabled controls & placeholder text | `--muted-foreground` at 50% opacity |
| Text on lime green buttons/badges | `--primary-foreground` |
| Text on destructive badges | `oklch(1 0 0)` (pure white) |
| Sidebar item labels | `--sidebar-foreground` |
| Active sidebar item label | `--sidebar-primary-foreground` |

---

## 4. Spacing System

Tailwind's standardized 4px grid scale governs all interface rhythm:

| Token | Value | Common Usage in IDX Copilot |
|---|---|---|
| `space-1` | 4px | Gaps between ticker status dots and symbols, tight badge margins |
| `space-2` | 8px | Inside badge padding, tight table cell gaps, quick-chip margins |
| `space-3` | 12px | Button vertical padding, gap between navigation icon and label |
| `space-4` | 16px | Card padding, standard horizontal gutter |
| `space-5` | 20px | Section inner card padding, prominent financial metric boxes |
| `space-6` | 24px | Grid gap between comparison cards, major report section splits |
| `space-8` | 32px | Separation between executive summary and deep-dive sections |
| `space-10` | 40px | Major page canvas vertical rhythm |

### Component-Specific Spacing

| Component | Applied Classes | Notes |
|---|---|---|
| Research Card | `p-4` (16px) or `p-5` (20px) | `p-5` preferred for primary valuation and driver panels |
| Button (Default CTA) | `px-4 py-2` (16px / 8px) | "Analyze Request", "Compare Stocks" |
| Button (Compact) | `px-3 py-1.5` (12px / 6px) | Inline table actions, "Add to Watchlist" |
| Badge / Ticker Pill | `px-2.5 py-0.5` (10px / 2px) | Stock badges, valuation verdicts, flow tags |
| Sidebar Navigation Item | `px-4 py-3` (16px / 12px) | Full-width item with icon + label |
| Table Cell | `px-4 py-3` (16px / 12px) | Screener & historical financial data tables |
| Form Input / Textarea | `px-3 py-2` (12px / 8px) | Search inputs, prompt composer textarea |
| Modal / Dialog Panel | `p-6` (24px) | Ticker inspector, delete confirmations |
| Main Canvas Area | `p-6` to `p-8` (24px to 32px) | `px-4 py-6 sm:px-6 lg:px-10 lg:py-10` |

---

## 5. Border Radius & Shape

```css
--radius: 1rem; /* 16px — standard base radius */
```

### Radius Scale

| Name | Computed Value | Usage in IDX Copilot |
|---|---|---|
| `rounded-none` | 0 | Never used — eliminates sharp raw edges |
| `rounded-sm` | 4px | Small code tags, micro data freshness indicators |
| `rounded` | calc(var(--radius) - 8px) = 8px | Form inputs, keyboard shortcut keys (`<kbd>`) |
| `rounded-md` | calc(var(--radius) - 4px) = 12px | Default buttons, dropdown menus, filter selects |
| `rounded-lg` | var(--radius) = 16px | **Primary radius: All analytical cards, prompt composer** |
| `rounded-xl` | calc(var(--radius) + 4px) = 20px | Modals, execution trail drawers, floating panels |
| `rounded-full` | 9999px | Ticker badges, status dots, prompt template chips |

### Shape Rules

- **Research Cards:** Always `rounded-lg` (16px)
- **Prompt Composer Box:** `rounded-lg` (16px)
- **Buttons:** `rounded-md` (12px) for standard buttons, `rounded-lg` (16px) for large CTAs
- **Search & Text Inputs:** `rounded` (8px) or `rounded-lg` (16px for prominent composer textarea)
- **Ticker Badges & Status Pills:** Always `rounded-full`
- **Status & Indicator Dots:** `rounded-full`, 6px × 6px or 8px × 8px
- **Sidebar Canvas:** Flat rectangular edge against viewport; navigation items inside use `rounded-lg`
- **Modals & Drawers:** `rounded-xl`
- **Tooltips & Popovers:** `rounded-md`

---

## 6. Shadow System

Shadows utilize the CSS variables as blur radius on `var(--card)` with low opacity. In dark mode, depth is established through layer luminosity (`--background` vs `--card` vs `--popover`) rather than heavy black dropshadows.

```css
--shadow-xs:  1px;
--shadow-md:  1.5px;
--shadow-lg:  2px;
--shadow-xl:  2.5px;
--shadow-2xl: 3px;
```

| Level | Usage in IDX Copilot |
|---|---|
| **No Shadow** | Standard static research cards (contrast provided by `--card` and `--border`) |
| `shadow-sm` | Focused search inputs, active prompt chips |
| `shadow-md` | Autocomplete ticker dropdown, screener filter popovers |
| `shadow-lg` | Agent execution trail drawer, report confirmation modals |
| `shadow-xl` | Floating toast notifications ("Added to Watchlist") |

---

## 7. Layout

### Terminal Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Desktop Sidebar (256px fixed) │  Main Research Canvas                      │
│  --sidebar background          │  --background                              │
│                                │                                            │
│  [IDX Copilot Brand]           │  [Top Header: Breadcrumb & Market Status]  │
│                                │                                            │
│  RESEARCH TOOLS                │  [Prompt Composer / Analysis Trigger]      │
│  • New Analysis (Workspace)    │                                            │
│  • Dashboard                   │  [Executive Summary & Ticker Badges]       │
│  • Compare Stocks              │                                            │
│  • Screener                    │  [Metric Grid: Valuation / Foreign Flow]   │
│                                │                                            │
│  PORTFOLIO & HISTORY           │  [Bullish Drivers vs Bearish Risks Grid]   │
│  • Saved Reports               │  [Flow Divergence & Histogram Charts]      │
│                                │                                            │
│  [Ctrl+Enter Shortcut Helper]  │  [Verified Data Citations & Follow-up Q&A] │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Sidebar width:** 256px (`w-64`), sticky to viewport height (`h-screen sticky top-0`)
- **Main content area:** `flex-1 min-w-0`, vertical scrolling
- **Content padding:** `px-4 py-6 sm:px-6 lg:px-10 lg:py-10`
- **Max layout constraint:** `max-w-7xl` or responsive fluid container

### Grid System

Content grids align financial metrics into scannable columns:

```css
/* Overview Metric Cards (P/E, P/B, ROE, Foreign Flow) */
grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));

/* Catalyst Split: Bullish Drivers vs Bearish Risks */
grid-template-columns: repeat(2, minmax(0, 1fr)); /* stacks to 1fr on mobile */

/* Multi-Stock Peer Comparison Matrix */
grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));

/* Main Report + Agent Execution Trail split */
grid-template-columns: 1fr 340px;
```

Standard grid gap: `gap-6` (24px) for cards; `gap-4` (16px) for dense metric tables.

---

## 8. Component Theming

### 8.1 Sidebar Navigation

```
Background:    --sidebar
Text:          --sidebar-foreground
Active item:   --sidebar-primary (lime green bg) + --sidebar-primary-foreground (dark text)
Hover item:    --sidebar-accent (elevated dark) + --sidebar-accent-foreground (white)
Divider:       --sidebar-border (subtle border between groups)
```

**Nav item anatomy:**
- Padding: `px-3 py-2.5`
- Border radius: `rounded-lg`
- Icon: 20px × 20px, matches foreground
- Active state: Lime green background with bold dark text (`text-slate-950 font-semibold`)
- Hover state: `--sidebar-accent` (`bg-surface-950/60`), transition 150ms
- Group header: `text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 mb-2`

### 8.2 Research Cards

```
Background:       --card
Text:             --card-foreground
Border:           1px solid --border
Border radius:    rounded-lg (16px)
Padding:          p-5 (20px)
```

**Card variants in IDX Copilot:**

| Variant | Background | Border | Primary Role |
|---|---|---|---|
| **Standard Metric** | `--card` | `--border` | Financial ratios, P/E, P/B, Market Cap |
| **Bullish Catalyst** | `oklch(0.22 0.05 140 / 0.2)` | `oklch(0.40 0.12 140 / 0.5)` | Revenue growth, margin expansion drivers |
| **Bearish / Risk** | `oklch(0.22 0.06 25 / 0.2)` | `oklch(0.42 0.15 25 / 0.5)` | Debt headwind, regulatory or forex risk |
| **Divergence Alert** | `oklch(0.24 0.06 70 / 0.2)` | `--warning` | Smart money vs retail price divergence |
| **Citation Drawer** | `--muted` | `--border` | Verified Sectors API endpoints & timestamps |

### 8.3 Buttons & Actions

| Variant | Background | Text | Hover State | Purpose |
|---|---|---|---|---|
| `primary` | `--primary` (lime) | `--primary-foreground` | `--primary-dark` | "Analyze Request", "Compare Stocks" |
| `secondary` | `--secondary` | `--secondary-foreground` | `--muted-dark` | "Add to Watchlist", template prompt chips |
| `destructive` | `--destructive` | white | `--destructive-dark` | "Delete Report", "Remove Stock" |
| `outline` | transparent | `--foreground` | `--muted` | "Export PDF", "Reset Filters" |
| `ghost` | transparent | `--muted-foreground` | `--muted` + white text | In-field clear `X`, icon-only buttons |

**Action Button Sizes:**
- `sm`: 32px height, `px-3 py-1.5`, `text-xs`, `rounded`
- `default`: 40px height, `px-4 py-2`, `text-sm`, `rounded-md`
- `lg`: 48px height, `px-6 py-2.5`, `text-sm font-semibold`, `rounded-lg`

### 8.4 Badges & Status Indicators

All badges use `rounded-full`, `px-2.5 py-0.5`, and font size `text-xs`.

| Badge | Background | Text | Semantic Purpose |
|---|---|---|---|
| **Ticker Pill** | `--card` | `--primary` | Identifies IDX stock symbols (`BBCA`, `TLKM`) |
| **Undervalued** | `--primary` | `--primary-foreground` | Valuation discount verdict |
| **Fair Value** | `--warning` | white | Neutral valuation status |
| **Overvalued** | `--destructive` | white | Valuation premium / warning |
| **Foreign Inflow** | `--primary` | `--primary-foreground` | Net institutional buying accumulation |
| **Foreign Outflow** | `--destructive` | white | Net institutional distribution |
| **Data Freshness** | `--muted` | `--muted-foreground` | Live vs cached timestamp |

### 8.5 Financial Data Tables

Used in Stock Screener, Multi-Stock Comparison, and Historical Statements.

```
Header:       --muted background, --muted-foreground text, text-xs uppercase tracking-wider
Rows:         Alternating --card and transparent backgrounds
Row Hover:    --muted background, transition-colors duration-100
Borders:      1px solid --border along row bottoms (border-b)
Cell Padding: px-4 py-3
Alignment:    Left-align ticker and name; right-align all currency, ratios, and percentages
```

### 8.6 Forms & Prompt Composer

```
Textarea Background:  --background (recessed below card level)
Textarea Border:      --input (1px solid --border)
Textarea Text:        --foreground (crisp white)
Placeholder:          --muted-foreground (subtle grey)
Focus State:          ring-2 ring-[--ring] (lime green ring, no default black outline)
```

**Search Field with In-Field Clear (`X`):**
- Input container: `relative flex items-center`
- Input: `w-full bg-background border border-border rounded px-3 py-2 pr-8 text-sm`
- Clear button: Positioned right inside input (`absolute right-2.5 top-1/2 -translate-y-1/2`), ghost styling, toggles visible on input entry.

### 8.7 Modals & Drawers

```
Backdrop Overlay:  black at 60% opacity with backdrop-blur-sm
Panel Canvas:      --card
Panel Border:      1px solid --border
Border Radius:     rounded-xl (20px)
Padding:           p-6 (24px)
Elevation:         shadow-lg
```

- **Execution Trail Drawer:** Slides from right or anchors beneath report with live status badges, API latency measurements, and timestamped citations.
- **Delete Confirmation:** Explicitly names the report or ticker being removed, destructive button requires deliberate click.

### 8.8 Toast Notifications

Anchored top-right (`z-50`, `max-w-sm`):
- **Success (Lime left border 4px):** Stock added to watchlist, report exported.
- **Warning (Orange left border 4px):** Query out-of-scope, rate limit approaching.
- **Error (Red left border 4px):** Upstream API 503, invalid stock ticker.
- Auto-dismiss: 4,000ms (success), 6,000ms (errors).

### 8.9 Financial Visualizations & Charts

1. **Zero-Dependency SVG Price Sparklines:**
   - 20-session daily closing price converted into an SVG `<polyline>`.
   - Stroke: `--primary` (lime green) if latest price >= initial; `--destructive` (red) if negative trend.
   - Background: Transparent container with subtle grid reference line.

2. **Tailwind Net Foreign Flow Histograms:**
   - 14-session vertical bars indicating daily foreign transaction volume.
   - Positive inflow: Emerald/lime `--primary` bar extending upward.
   - Negative outflow: Red `--destructive` bar extending downward.
   - Hover state displays tooltip with exact IDR volume and broker accumulation balance.

3. **Valuation Benchmark Charts:**
   - Base bars: `--muted`
   - Active stock bar: `--chart-1` (`--primary` lime green)
   - Industry median line: `--chart-4` dashed rule

---

## 9. Interaction States

Every interactive element must implement all interaction states:

| State | Concrete Visual Implementation |
|---|---|
| **Default** | Base token values (`--card`, `--primary`, `--border`) |
| **Hover** | Background shifts to `--*-dark` or `--muted`, `transition-colors duration-150` |
| **Focus Visible** | `ring-2 ring-offset-2 ring-[--ring]` (lime green). Never remove outline without ring |
| **Active / Pressed** | Micro-scale compression: `scale-[0.98] transition-transform` |
| **Disabled** | `opacity-50 cursor-not-allowed pointer-events-none` |
| **Loading** | Animated spinner icon + disabled state + elapsed timer |
| **Selected** | `--primary` background with dark text, or `--primary` border highlight |
| **Validation Error** | `--destructive` border and helper text below input |

---

## 10. Responsive Breakpoints

| Breakpoint | Viewport Width | Layout Adaptation |
|---|---|---|
| `sm` | ≥ 640px | Stat cards switch to 2-column grid |
| `md` | ≥ 768px | Prompt composer template chips expand to full row |
| `lg` | ≥ 1024px | **Fixed desktop sidebar activates (256px)**; comparison grid opens 2-column |
| `xl` | ≥ 1280px | Full institutional research view with dual catalyst panels |
| `2xl` | ≥ 1536px | Max-width content boundary kicks in (`max-w-7xl`) |

**Mobile Devices (< 1024px):**
- Sidebar collapses into an off-canvas Flowbite drawer (`#mobile-drawer`).
- Quick navigation bar anchors to bottom of screen (`bottom_nav.html`).
- Metric tables become horizontally scrollable with `overflow-x-auto`.
- Multi-stock comparison cards stack into a single column.

---

## 11. Motion & Animation

IDX Copilot is an intensive data analysis tool. Animations must be purposeful, snappy, and restrained.

| Interaction | Duration | Easing | Description |
|---|---|---|---|
| Nav item hover | 150ms | `ease-in-out` | Background color crossfade |
| Ticker dropdown pop | 150ms | `ease-out` | Subtle 4px slide-down + opacity fade |
| Modal panel enter | 200ms | `ease-out` | Scale 95% → 100% + backdrop blur |
| Toast slide-in | 300ms | `ease-out` | Horizontal slide from right edge |
| Button press | 100ms | `linear` | `scale(0.98)` tactile feedback |
| Loading spinner | Continuous | `linear` | Smooth infinite rotation |
| Agent status pulse | 1500ms | `ease-in-out` | Opacity 1 → 0.4 → 1 on active indicator dot |

**Prohibited:**
- Bouncing spring animations.
- Animation durations exceeding 350ms.
- Movement shifting content by more than 8px.

---

## 12. Accessibility

- **Focus Visibility:** All interactive elements must show a distinct focus ring (`focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none`).
- **Contrast Ratios:** Text on `--card` and `--background` strictly adheres to WCAG AA (minimum 4.5:1 for standard body copy, 3:1 for large display text).
- **Semantic HTML:** Buttons use `<button>`, links use `<a>`, financial figures use `<data>` or `<span class="font-mono">`.
- **Screen Reader Support:** Status dots and icon-only buttons include `<span class="sr-only">` or `aria-label`.
- **Keyboard Navigation:** Full workflow executable via keyboard (Prompt submission via `Ctrl+Enter`, tab-navigable chips and citation links).
- **Reduced Motion:** Respects user system preference `prefers-reduced-motion: reduce`.

---

## 13. Template & Component Conventions

When authoring or modifying Django templates in `templates/*` or `src/research/templates/*`:

```html
<!-- ✅ Correct — token-driven, semantic, consistent -->
<div class="rounded-lg border border-slate-800 bg-surface-900 p-5 shadow-panel">
  <span class="inline-flex items-center gap-1 rounded-full bg-brand-950 border border-brand-800 px-2.5 py-0.5 text-xs font-mono font-bold text-brand-400">
    <span class="h-1.5 w-1.5 rounded-full bg-brand-500"></span>
    BBCA
  </span>
  <h3 class="mt-3 text-lg font-semibold text-white">Analisis Valuasi & Flow</h3>
</div>

<!-- ❌ Wrong — hardcoded hex styles or custom paddings -->
<div style="background-color: #1a1b26; border-radius: 13px; padding: 19px;">
  <span style="color: #00ff00;">BBCA</span>
</div>

<!-- ❌ Wrong — overriding standardized tokens with aggressive custom colors -->
<div class="bg-purple-900 rounded-none p-12">
```

**Rule:** Every visual element must be composed using the color variables, radius scale, and spacing tokens outlined in this document. Never introduce one-off colors or non-standard border radiuses.

---

*Last updated: September 2026 — Sectors Hackathon 2026 (AI IDX Investment Research Copilot)*
