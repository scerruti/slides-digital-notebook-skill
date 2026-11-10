---
name: slides-digital-notebook
description: Build, audit or explain a tabbed "digital notebook" in Google Slides - portrait pages with colored, clickable section tabs down the right edge, color-coded divider pages, and a published read-only link (the format of the CSTA Leader Toolkit and SlidesMania notebooks). Use this whenever someone wants a resource guide, handbook, toolkit, employer/partner/parent guide, onboarding binder or other reference material "like a binder with tabs", "with clickable tabs", "interactive notebook" or "one place with everything linked" in Google Slides; when they want to add pages or sections to such a deck or check its tabs and links; or when they need instructions telling a team how to format and publish one. Also use it to judge whether that format fits some content at all, even if they never say "notebook".
---

# Google Slides digital notebook

A digital notebook is a Google Slides deck that works like a tabbed binder instead of a presentation:

- portrait pages, about 7.5 x 10 in
- one colored tab per section down the right edge of every page, each linked to that section's divider page
- a divider page per section: a full-width band in the tab's color with the section name
- the current section's tab sticks out slightly further than the others
- every resource is a clickable link
- readers get the **published** link (File > Share > Publish to web), which opens a clean viewer where the tabs work on one click

Readers jump straight to the one task they came for and trust that the link always shows the current version.

## First, check the format fits

The format suits **reference material that changes occasionally**: guides, toolkits, handbooks, FAQs. It fits poorly when the content grows every day, like a running class deck with a new day of slides each lesson. Every new page needs its tabs and links, and a rolling set of date tabs never stays current. If the content is like that, say so and suggest something lighter: a single linked contents or calendar slide, a script that rebuilds the index, or splitting the deck.

Keep to **8 tabs or fewer**. More than that won't fit readably down one edge. When the material has more topics than that, group related topics under one tab (several pages behind one divider), or fold rarely used material into a "Resources" tab. Show the user the grouping rather than dropping topics. Splitting into several notebooks is for different audiences, not for having too many topics.

## Start from the content, not a structure

Don't ask writers to fit their material into a folder layout or template before you've seen it. Read what they have first, whatever form it's in: a repo of Markdown, Docs, a PDF, notes. Then propose the notebook:

- **Who it's for.** If the material serves different readers (for example employers, students and school staff), propose one notebook per audience rather than audience tabs in one deck. Audience tabs use up the 8-tab budget and make every reader skip pages that aren't theirs.
- **Tabs.** Group the material by what readers come to do, in the order they'll need it, using the writers' own headings where they work. Note what doesn't fit.
- **Pages.** One task per page. Point out pages that need splitting or merging, rather than silently rewriting them.
- **Gaps and overlaps.** List missing pieces (contacts, dates, links) and content that repeats across manuals.
- **Dates.** Flag calendar dates (end dates, closures, deadlines) and propose replacing them with a durable rule plus a pointer to wherever dates are maintained (a calendar link or the person to ask). Dates in a guide need yearly edits, go stale silently, and copies drift apart.
- **Who owns the published link.** The published address belongs to the Google account that publishes the deck, and it changes if the deck is ever re-created elsewhere. Ask which account (ideally a shared or organizational one, not a person's) should own each notebook, before building in someone's personal Drive.

Show that mapping as a short table (tab → pages → source) and get the user's OK before building. The writers' structure is the default. Only depart from it with a reason the user agrees to.

## Several notebooks in one family

When there are several related notebooks (separate manuals for different audiences):

- **Specs and IDs.** Give each its own spec and its own `prefix` (`emp`, `sch`, `adm`), so slide IDs never collide and stay predictable.
- **Shared look.** Same page size, layout, fonts and strip width across all of them. A section that appears in several notebooks (Getting started, FAQ, Contacts) keeps the same label, color and tab position in each, and each notebook gets its own cover color.
- **Shared content.** Material used in more than one notebook should have one source. When it changes, update every notebook that uses it.
- **Linking between notebooks.** A published deck opens at a given page when `&slide=id.<page id>` is added to its published link (the address bar shows this form as you click through the Toolkit). Test such a link once before relying on it. The predictable IDs from this script keep those links stable through rebuilds.

## Building with the Google connectors

Read the `google-workspace` skill's Slides reference first if it's available. Its rules apply here: masked reads, `writeControl.requiredRevisionId` from a fresh read before each guarded write, and checking the result after each write.

`scripts/notebook.py` turns a short spec into the request batches, so the geometry and link order never get worked out by hand. Write the spec:

```json
{"prefix": "nb",
 "tabs": [{"id": "start", "label": "Getting started", "color": "#1565C0"},
          {"id": "post",  "label": "Posting a role",  "color": "#F9A825"},
          {"id": "faq",   "label": "FAQ",             "color": "#2E7D32"}],
 "font_size": 10, "strip": 0.45, "dividers": true}
```

Tab labels should be 1-3 words, because they're set at 10 pt along a tab about 1 in long. The script picks white or dark label text for each color by contrast.

### 1. Get a portrait deck

The connectors can't change a deck's page size, but Drive converts an uploaded .pptx at whatever size it has. For a new notebook, make the deck yourself:

```
python scripts/portrait_pptx.py blank.pptx --b64 blank.b64      # 7.5 x 10 in; --width/--height for other sizes
```

Then call Drive `create_file` with the deck's title, `contentMimeType` `application/vnd.openxmlformats-officedocument.presentationml.presentation` and `base64Content` = the contents of `blank.b64` (about 5.6 KB). The result is a portrait Google Slides deck with one blank slide (use it as the cover) and a plain Arial theme. The script needs only the Python standard library.

If the user wants to use a deck they already have, it must already be portrait. Ask them to set **File > Page setup > Custom > 7.5 x 10 in**, or to start from a portrait template such as a SlidesMania "digital notebook", keeping its credit line. Don't resize a deck that already has content: Slides stretches everything on it.

The script reads the page size from the deck, so it works on any size. Landscape only gets a warning from `check`.

### 2. Skeleton: template page, dividers, linked tabs

Read the deck with a mask that includes `revisionId,pageSize,slides.objectId`, save it to a file, then run:

```
python scripts/notebook.py skeleton spec.json --deck read.json --revision <revisionId> [--index 1]
```

Send the printed body to `update_presentation` exactly as printed. It does the following, in an order that matters:

1. draws the tab strip on a template page (`<prefix>_tpl`)
2. copies the template into one divider per tab (`<prefix>_div_<tab id>`)
3. only then links every tab on every page
4. adds each divider's color band and title, and nudges its own tab out
5. moves the dividers to `--index` (default 1, right after the cover)
6. marks the template as skipped, so readers never see it

The order is there because of how Google behaves. A slide copied while one of its tabs links to a page that doesn't exist yet gets a broken, made-up link target. A slide copied after its links' targets exist keeps working links. So never link to pages that don't exist yet and copy afterwards.

### 3. Content pages

```
python scripts/notebook.py pages spec.json --section post --count 3 --index <slide index> [--start 1] --revision <revisionId> --deck read.json
```

This makes copies of the template (IDs like `nb_post_1`), nudges the section's tab out, un-skips the copies and moves them to `--index`. Put them right after that section's divider or its last page. Copying is the whole trick: a copy carries the full tab strip with working links. A blank "New slide" has no tabs. Use `--start` to keep IDs unique when adding to a section that already has pages. With `--deck` (a fresh read with `revisionId,pageSize,slides.objectId`), the script first checks that the template exists and the new IDs are free, and suggests the right `--start` if not.

Then fill the pages with the normal Slides tools, for example `slides_helper.py build` with `"existing": true`. Pass it **`--page 7.5x10`** (or the deck's real size): it assumes a 10 x 5.625 in landscape page otherwise, and its off-page and text-fit warnings are then wrong. Keep everything inside the **safe area the skeleton command prints** (x from 0.5 in to about W - 0.75 in). Anything reaching into the right-hand strip sits on top of the tabs and blocks clicks.

**When a page's content doesn't fit**, don't shrink the text below the helper's minimum or let it run off the page. Split it: make another page in the section (`pages --count 1 --start <next>`) and move the rest there, with the same heading plus "(continued)" or a more specific one. The helper's "text likely needs ~X in of height" warning is the signal. Confirm with a thumbnail of the page.

#### Images and screenshots

Many guides are mostly screenshots. Slides `createImage` fetches the image from a URL **once, at insertion**, and keeps its own copy, so the source can go away afterwards. The URL must:
- be reachable **without signing in** (a domain-only or "restricted" Drive link fails, because the fetch isn't signed in)
- return the image itself, not a viewer page
- point to a PNG, JPEG or GIF under 50 MB and 25 megapixels, with a URL under 2 KB

Place each image with the script, which boxes it inside the safe area. Slides scales the image to fit the box and keeps its aspect ratio, so a tall phone screenshot is limited by the height and centered:

```
python scripts/notebook.py image spec.json --page nb_post_2 --id nb_post_2_img1 --url <URL> --y 1.6 [--h 5] --deck read.json --revision <revisionId>
```

Put the text above (or below) at a `y` that leaves the image room, and check a thumbnail. Name the image after its page (`<page>_img1`); never end an ID in `_t<number>`, which is how `check` spots tabs.

**Images that aren't on a public site yet: temporary Drive hosting.** Ask the user before changing any sharing.
1. The user drags the images into one Drive folder. That avoids passing dozens of screenshots through the conversation as base64.
2. Note each file's current sharing, then set the files to "Anyone with the link can view". Workspace domains often block this. If they do, stop and say so; the user has to host the images somewhere public instead, or insert them by hand (Insert > Image > Drive works signed in).
3. Insert **one** image first with `https://drive.google.com/uc?export=download&id=<fileId>`. If that fails, try `https://drive.google.com/thumbnail?id=<fileId>&sz=w1600`. Neither form is documented by Google, so test before doing the rest, and stop if neither works.
4. Insert the rest the same way, then check the thumbnails.
5. Put each file's sharing back the way it was, or trash the files if the user agrees. The deck keeps its copies either way.

Cover page (slide 1): the title, an "Updated <month year>" line and the logo. It needs no tabs. A short "How to use this guide" line helps: click a tab to jump; click underlined text to open it.

### 4. Check

Read the deck again with `revisionId,pageSize,slides(objectId,slideProperties.isSkipped,pageElements(objectId,size,transform,shape(shapeProperties.link),elementGroup))`, save it, and run:

(The Slides connector accepts this parenthesized mask, unlike Sheets. The flat form, `slides.pageElements.objectId,slides.pageElements.size,...`, works too. On a large deck the result is too big to show inline, so save it to a file rather than reading it. `isSkipped` lets the check tell hidden pages from real ones; `elementGroup` lets it see grouped elements.)

```
python scripts/notebook.py check spec.json read.json
```

It reports:
- pages with missing tabs, or no tab strip at all
- tabs linking to deleted pages, or to the wrong section
- anything drawn on top of a tab, rotated and grouped elements included (a background sent behind the strip is fine)
- pages that are skipped, so readers never see them
- tab colors whose labels fall below 4.5:1 contrast
- a landscape page

A contents list on the cover that links to dividers is fine; only shapes in the right-hand strip count as tabs.

Fix everything it reports, then look at one rendered divider and one content page (`read_slide_page_thumbnail`) before telling the user it's done.

### What only the user can do

- **Publish.** The connectors can't publish to the web. Give the user the steps in `references/team-guide.md` (Publishing).
- **Test the clicks.** Links only respond in Slideshow or the published view, which you can't open signed in. Ask the user to click every tab once in the published link.

## Working on an existing notebook someone else built

Read it, then infer the spec from the tab shapes: their labels, colors and link targets. If its IDs don't follow this script's naming, don't force them to. Add pages by copying one of its own content pages with `duplicateObject`, after its link targets exist, then move the copy's active tab. `check` finds hand-made tabs by their position in the right-hand strip, but it needs the dividers to be named `<prefix>_div_<tab id>`. When they aren't, compare the link targets on each page yourself.

## Writing instructions for a team

When the user wants people to build or maintain a notebook by hand, write them a document. Base it on `references/team-guide.md`, which covers:
- why the format
- file setup
- building and linking tabs
- color and layout rules
- writing and linking content
- publishing
- upkeep
- a pre-publish checklist

Adapt the section names, examples and owner to their project rather than pasting it whole.
