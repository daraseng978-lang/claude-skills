# Platform Specs — FB / IG / TikTok Reels

Reference for `funny-reels` skill. Last reviewed: 2026-04.

## Dimensions (all platforms)

- **Aspect ratio:** 9:16
- **Resolution:** 1080 × 1920 (minimum), 1080p preferred
- **Frame rate:** 30 fps (60 fps OK, don't go lower than 24)
- **Codec:** H.264, AAC audio
- **File size cap:** ~500 MB safe across all three

## Length Sweet Spots

| Platform | Min | Max | Sweet spot | Notes |
|----------|-----|-----|-----------|-------|
| TikTok | 3s | 10 min | 15-30s | >60s reels need stronger story arc |
| Instagram Reels | 3s | 90s | 15-30s | <15s feels undercooked for the algo |
| Facebook Reels | 3s | 90s | 30-60s | Slightly older audience → can tolerate slower setup |

**Rule:** shoot once at 30-35s → export trimmed variant per platform.

## Safe Zones (where NOT to put key text/jokes)

Each platform overlays UI on top of your video. Never place critical text/faces in these regions:

### TikTok
- **Top:** 130px (username, "For You" label)
- **Right side:** 180px wide (like/share/comment stack)
- **Bottom:** 340px (caption, sound, progress bar)

### Instagram Reels
- **Top:** 220px (profile, "Reels" badge)
- **Right side:** 140px (action stack)
- **Bottom:** 400px (caption, music, profile)

### Facebook Reels
- **Top:** 180px
- **Right side:** 160px
- **Bottom:** 380px (caption + FB's extra CTA buttons)

**Use the largest of the three** → top 220px + right 180px + bottom 400px clear of key content if you're cross-posting one master file.

## Captions & Text

- **Always burn in captions** — ~85% of viewers watch muted.
- **Font:** bold sans-serif (Inter, Poppins Bold, TikTok Classic)
- **Color:** white with 4px black stroke OR solid color background bar
- **Line length:** max 32 chars per line, 2 lines max on screen at once
- **Timing:** each caption on screen ≥ 1.2s (readable), ≤ 3s (don't linger)

## Audio

- **TikTok:** strong bias toward trending sounds < 7 days old. Tag the sound.
- **Instagram:** trending audio works but original audio builds character/franchise.
- **Facebook:** original audio or licensed library — FB detects and mutes flagged audio aggressively. Avoid chart music unless licensed via FB's library.

## Cover Frames (thumbnails)

- **Instagram:** cover appears on grid + Explore. Choose frame with bold text hook and face in focus. Don't use pure title cards — looks like spam.
- **TikTok:** cover matters less (FYP autoplays), but profile-grid browsers still see it. Use a frame with text + expression.
- **Facebook:** cover appears in feed. Same rules as Instagram.

## Posting Times (rough averages — always AB test)

| Platform | Best windows (local time) |
|----------|--------------------------|
| TikTok | Tue-Thu 6-10 AM, 7-11 PM |
| Instagram | Mon-Fri 11 AM-1 PM, 7-9 PM |
| Facebook | Wed-Fri 1-4 PM (older audience, lunch/afternoon) |

## Hashtag Rules

| Platform | Count | Placement | Strategy |
|----------|-------|-----------|----------|
| TikTok | 3-5 | Caption | 1 broad + 2 niche + 1 trend |
| Instagram | 5-10 | First comment | Mix size buckets: 1 huge, 3 mid, 3 small |
| Facebook | 2-3 | Caption | FB hashtags barely work — used for brand, not reach |

## What Kills Reach

- Watermarks from other platforms (TikTok detects IG watermark, IG detects TikTok logo, FB detects both)
- Posting the exact same file within 24h across platforms (algorithm flags)
- Low-res upload (< 720p)
- No captions → lower completion rate → lower push
- First 3s has a logo/sting/intro card → instant scroll

## Export Workflow (recommended)

1. **Master:** 1080×1920, 30s, captions burned in, no watermark.
2. **TikTok export:** trim to 20s, add trending sound overlay, upload.
3. **IG export:** 25s, keep original audio OR swap to trending IG track, upload.
4. **FB export:** full 30s, front-loaded hook (cut 0.5s off the setup), upload.

Stagger posting by 2-4 hours minimum across platforms.
