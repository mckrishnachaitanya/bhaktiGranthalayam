# భక్తి గ్రంథాలయం (Bhakti Granthalayam) — Handover

**Status: CURRENT** (as of this session)

## Objective
A devotional reading PWA for Krishna's mother — conceived as a "library" of devotional texts, not a single-book app. First (and currently only) book: **Sri Sai Satcharitra in Telugu**, chapter-wise, plus associated prayers/aartis. Built to the same pattern as Vault/PaisaTrail: single-file vanilla JS, no build step, GitHub Pages hosting, installable PWA.

Future books will be added to this same app (see Open Items). The name and icon were deliberately chosen to not be Satcharitra-specific.

## Repo
GitHub: `mckrishnachaitanya/app-group` (same multi-app repo pattern as other PWAs)
Live URL: `https://mckrishnachaitanya.github.io/app-group/` *(confirm exact path/subfolder if this app lives in a subdirectory — not yet independently verified)*

## Files in repo (root)
| File | Purpose |
|---|---|
| `index.html` | The entire app — chapter list, reader, settings sheet, all JS/CSS inline. **Just patched this session** — see "Recent fix" below. |
| `chapters.json` | Scraped content: 54 entries — 51 Satcharitra chapters (3 pages combine 2 chapters each) + closing shlokas + 4 daily aartis. Confirmed correct/complete this session. |
| `manifest.json` | PWA manifest — name "భక్తి గ్రంథాలయం", short name "భక్తి", references `icon-192.png`/`icon-512.png` |
| `sw.js` | Service worker — cache-first offline. **Critical**: `VERSION` const must be bumped every time `index.html`/`manifest.json`/icons change, or the browser won't detect an update and installed copies (like on Krishna's mother's phone) will keep serving stale cached files indefinitely. **Verify this was bumped after today's index.html fix.** |
| `icon-192.png`, `icon-512.png` | App icons — final approved "pile of books" design (teal/maroon/cream/gold stack with bookmark ribbon) on maroon gradient |
| `scrape_satcharitra.py` | One-time scraper (Telugu text from funnotes.net) — kept in repo for reference/re-scraping, not used at runtime |
| `.github/workflows/scrape.yml` | Manual-trigger GitHub Action that runs the scraper server-side and commits `chapters.json` |

## Content structure (confirmed this session)
`chapters.json` array (54 entries, index 0–53) breaks down as:
- **index 0**: Parayananantara Slokamulu (closing shlokas, read after parayana)
- **index 1**: Saibaba Mangala Harathulu (morning aarti)
- **index 2–49**: Chapter 1 through Chapter 51 (48 pages — 3 pages each combine two chapters: "16 & 17", "18 & 19", "43 & 44")
- **index 50–53**: Kakad Harathi, Madhyahna Harathi, Dhoop Harathi, Shej Harathi (four time-of-day aartis)

Each chapter page's `paragraphs[0]` is a repeated book-name banner ("శ్రీ సాయి సత్ చరిత్రము"), not a real title — the actual heading is `paragraphs[1]` (e.g. "మొదటి అధ్యాయము"). Prayer/aarti pages don't have this banner; their `paragraphs[0]` is the real title.

## Recent fix (this session)
**Bug reported**: chapter list showed the same repeated title for every chapter, and day-grouping was wrong (count showed 54 instead of expected ~52, front-matter aarti appeared as "chapter 1").

**Root cause**: app read `paragraphs[0]` as the title (grabbing the banner instead of the real heading), and the day-split logic assumed json-index == chapter-number, which breaks because of the 3 combined-chapter pages and the 6 non-chapter entries mixed into the array.

**Fix applied** (client-side only in `index.html`, no re-scrape needed):
- Added a `prepChapters()` preprocessing step at load: detects the banner line and picks the correct title; parses `link_text` (e.g. "Chapter 16 & 17") to extract real chapter number(s) via regex; separates chapter pages from prayer/aarti pages.
- Day grouping (`DAY_SPLIT` = [1-7],[8-15],[16-22],[23-30],[31-37],[38-44],[45-51]) now buckets by actual chapter number, not array index.
- Non-chapter entries (slokas + 4 aartis) now render in their own bottom section: "పూజ మరియు హారతులు · Prayers & Aartis" — instead of being misfiled as chapters.
- Reader body now uses the correctly-sliced paragraph array (skips banner + heading, shows actual prose).
- **Verified** against the real uploaded `chapters.json` via a Node.js simulation before shipping: all 51 chapter numbers present exactly once, correct titles for all 54 entries, correct day buckets, correct 6-item prayers/aartis list.

## App features (implemented, unchanged from before)
- **Home**: "Continue reading" card, mala-bead progress strip, chapters grouped by parayana day + separate prayers/aartis section
- **Reader**: Noto Serif Telugu, 4 font sizes, 3 themes (light/sepia/dark), scroll position remembered per chapter, prev/next navigation
- **Mark as read**: manual button, returns to chapter list (no auto-advance)
- **Parayana reset**: "Start new saptaha" clears progress, logs completion date if all were read
- **Offline**: service worker precaches everything
- **Storage**: localStorage only, no backend/login
- **Language**: UI labels Telugu + English mix
- **Installable**: manifest + SW + HTTPS + PNG icons (192/512) for full Chrome install prompt

## Open items / next steps
1. **Confirm today's fix is live**: Krishna to upload the patched `index.html`, and — critically — bump `sw.js`'s `VERSION` string (e.g. to `"ssc-v4"`), or the update won't reach any already-installed copy of the app.
2. **Mother's phone**: after the version bump is deployed, she needs one online app-open to fetch the update; if it still shows stale content, remove and re-add to home screen.
3. **Bookshelf restructure (future, not started)**: adding book #2 needs real structural work, not just a new JSON drop-in:
   - A `books.json` manifest (id, title, own chapters file, whether it uses day-grouping or a flat list)
   - A shelf/home screen to choose a book before the existing chapter-list screen
   - localStorage keys namespaced per book (e.g. `read_<bookId>`) so progress doesn't collide across books
   - **Important, discussed explicitly**: each new book will likely need its own scrape + its own extraction-bug-fixing pass, since every source site has different quirks (today's banner/title bug was funnotes.net-specific, not a generalizable fix). Expect a similar scrape → inspect → patch cycle per book.
   - No second book chosen yet — Krishna to decide what/where before this gets designed.

## Krishna's working preferences (recurring across projects)
- No implementation narration during coding — just plan, then final summary of changed files
- Uses FROZEN/CURRENT handover docs to carry context across sessions
- Mobile-only Claude usage; GitHub Pages deploy via GitHub's own web/app UI or GitHub Actions (no local git access)
