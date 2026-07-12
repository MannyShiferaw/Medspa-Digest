# Youth Bar Industry Digest

A small Python tool that checks industry news sources every day, keeps
anything relevant to running a medical aesthetics clinic, and writes you a
markdown digest you can read in about 5 minutes.

No paid APIs are used anywhere in this tool. Summaries are the news
source's own snippet (lightly cleaned up), and relevance scoring is done
with a keyword/rule-based system you can tune yourself in `config.py` — not
an AI model.

## What it does, in plain terms

1. Fetches ~30 RSS feeds — official regulator feeds (Health Canada, FDA,
   EMA), a couple of trade publications, and a set of Google News searches
   tuned to each category (regulatory, clinical, financial, marketing,
   consumer trends, competitive, financing).
2. Remembers every item it's ever seen (in a local database) so the same
   story never shows up twice.
3. Scores each new item 1-5 for relevance to your business and tags it
   with a category and a rough location (Halifax/local, Canada, North
   America, or Global).
4. Throws away anything that scores below 3.
5. Writes everything that's left into a dated markdown file in `output/`.

## One-time setup

You need Python 3.10 or newer (check with `python3 --version` in Terminal).

```bash
cd "/Users/michelle/Documents/Youth Bar News Monitor"
python3 -m venv venv                 # creates an isolated Python environment
source venv/bin/activate             # activates it (do this every time you open a new Terminal)
pip install -r requirements.txt      # installs the 4 packages this tool needs
```

## Running it

```bash
cd "/Users/michelle/Documents/Youth Bar News Monitor"
source venv/bin/activate
python scanner.py run
```

That fetches everything, scores it, and writes
`output/digest-<today's date>.md`. Open that file in any text editor,
or in something like Obsidian/Notion if you want nicer markdown
rendering.

To test just one category while you're tuning things (much faster):

```bash
python scanner.py run --category regulatory
```

Valid category names: `regulatory`, `clinical`, `financial`, `marketing`,
`consumer`, `competitive`, `financing`.

### Heads up about the very first run

The first time you run this, each Google News search brings back its
recent history (up to 25 stories per search, capped on purpose — see
`MAX_ITEMS_PER_SOURCE` in `config.py`), so your first digest will be
noticeably bigger than a normal day's — expect somewhere in the low
hundreds of items across all 7 categories combined, not 5-minutes'-worth.
From the second run onward, the "already seen" memory kicks in and you'll
only get genuinely new stories, which is when this starts feeling like a
real daily digest.

## Tuning relevance (config.py)

Everything that controls what shows up lives in `config.py`:

- **`SOURCES`** — the list of feeds/searches. Add, remove, or edit the
  Google News search text here (the `google_news_url(...)` calls).
- **`KEYWORD_BOOSTS`** — words that bump an item's score up. If you
  notice the digest missing something obviously relevant, or including
  too much noise, this is the first place to look.
- **`MIN_RELEVANCE_TO_INCLUDE`** — currently 3. Raise it to 4 for a
  stricter/shorter digest, lower it to 2 for a broader one.
- **`MAX_ITEMS_PER_SOURCE`** — how many entries to pull per feed per run
  (default 25).

None of this requires touching the other `.py` files.

### A couple of known rough edges

- **Google News links** open a Google redirect page rather than the
  original article directly — that's just how Google News RSS works, not
  a bug. Clicking through still gets you to the real article.
- **"Business Financing" will often come up empty.** That's by design —
  general Canadian small-business-lending news rarely mentions medical
  aesthetics specifically, so it only shows up when a story actually
  connects the two. You asked for this one to be occasional, not forced.
- If any single source is down or its feed URL changes, you'll see a
  `[skip]` line in the terminal output for it and everything else keeps
  running — one broken feed never stops the whole scan.

## Running it automatically every day (cron)

macOS runs `cron` in the background even when Terminal isn't open. This
sets it up to run once a day automatically.

1. Open Terminal and type:
   ```bash
   crontab -e
   ```
   (This opens a text editor for your personal schedule. It'll likely
   open in `vim` — if you've never used vim, press `i` to start typing,
   and when you're done press `Esc` then type `:wq` and hit Enter to save.)

2. Add this line (runs every day at 7:00 AM):
   ```
   0 7 * * * cd "/Users/michelle/Documents/Youth Bar News Monitor" && ./venv/bin/python scanner.py run >> logs/cron.log 2>&1
   ```
   Change `0 7` to a different hour/minute if you want a different time
   (the format is `minute hour * * *`, 24-hour clock).

3. Create the `logs` folder so cron has somewhere to write its output:
   ```bash
   mkdir -p "/Users/michelle/Documents/Youth Bar News Monitor/logs"
   ```

4. Save and exit. Run `crontab -l` any time to see your current schedule,
   or `crontab -e` again to edit it.

Your Mac needs to be turned on (it can be asleep — cron on recent macOS
generally still fires on wake, but a machine that's fully shut off at
7 AM will just skip that day). Check `logs/cron.log` occasionally to
confirm it's running and to see any `[skip]` lines.

### Alternative: keep a process running instead of cron

If you'd rather not deal with `crontab`, `apscheduler` (already in
`requirements.txt`) can run the scan on a timer as a long-lived process.
This isn't wired up yet — say the word if cron feels like too much
fiddling and I'll add a `python scanner.py schedule` command instead. The
tradeoff: it only runs while that process/Terminal window is left open
(or you set it up as a background service), whereas cron runs
independently of any open windows.

## Publish to the web (GitHub Pages)

Instead of (or alongside) local cron, this can run entirely in GitHub's
cloud on a daily schedule and publish a real website — no dependency on
your Mac being on, awake, or having Full Disk Access. It also renders a
nicer page than the raw markdown file: `docs/index.html`, a rolling
7-day window of everything relevant, grouped by category.

Everything code-side is already built — `.github/workflows/daily-digest.yml`
runs the scanner daily and commits the results back to the repo, which
GitHub Pages then serves automatically. A few one-time steps only you
can do (they need your GitHub login):

1. **Create a new repo** at github.com — public, empty (don't check
   "Add a README"). Name it whatever you like, e.g. `youth-bar-digest`.

2. **Add this Mac's SSH key to your GitHub account** so it can push
   without you typing a password each time:
   - Go to GitHub → your profile photo → **Settings** → **SSH and GPG
     keys** → **New SSH key**
   - Paste in this public key (already generated, this is safe to share
     — it's the public half only):
     ```
     ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGjljs+IiABXIMkIyNYeR/oNGAUXZTKel/2zZJVd2FZl manny@youthbar.ca (youth-bar-digest)
     ```
   - Give it any title you like (e.g. "Youth Bar digest Mac") and save.

3. **Tell me the repo's SSH URL** (looks like
   `git@github.com:yourusername/youth-bar-digest.git` — GitHub shows it
   on the new repo's page under "…or push an existing repository") and
   I'll do the first push.

4. **Enable Pages** once that first push is in: repo → **Settings** →
   **Pages** → under "Build and deployment", set Source to **Deploy
   from a branch**, branch **main**, folder **/docs** → Save. GitHub
   will show you the live URL (something like
   `https://yourusername.github.io/youth-bar-digest/`) — it can take a
   minute or two to go live the first time.

After that, it runs on its own daily. You can also trigger it manually
any time from the repo's **Actions** tab → "Daily digest" → **Run
workflow**, useful for testing without waiting for the schedule.

Once this is live and confirmed working, local cron becomes redundant
(running both is harmless — de-duplication means no double entries —
but there's no reason to keep both going). Just delete the line from
`crontab -e` if you want to drop it.

## What's next (not built yet)

- **Email delivery** — once you're happy with what the digest contains,
  give me SMTP credentials (or a sending service) and I'll wire up
  emailing the digest to you instead of/alongside the file.
- **Better summaries** — right now summaries are just cleaned-up feed
  snippets. If that ever feels too thin, the Claude API could write
  genuine 1-2 sentence summaries for a small per-item cost — only if/when
  you want to approve that.
