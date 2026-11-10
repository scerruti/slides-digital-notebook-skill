# Team guide: formatting and publishing a digital notebook

Source material for instructions written for people who build or maintain a notebook by hand. Adapt the names, examples and owner to the project. The model to point people at is the CSTA Leader Toolkit:
https://docs.google.com/presentation/d/e/2PACX-1vRZyyUXuSyM3EYLijVxfdn6rng2r15F4ZNuKiq8jmUTFFZID0SmsNEDASo7qcSPmC0H3ilqdliRDE2i/pub?start=false&loop=false&delayms=3000

## Contents
1. Why this format
2. Set up the file
3. Build the tabs and links
4. Color and page layout
5. Writing and linking content
6. Publishing
7. Keeping it current
8. Pre-publish checklist

## 1. Why this format

Readers drop in for one task and leave. The notebook lets them find that task in one click and trust they're on the current version.

| Feature | What it does for the reader |
| --- | --- |
| One file, one link | Everything is in one place; nobody sends an "updated version". |
| Tabs on every page | The table of contents is always visible; any section is one click away. |
| Color coding | Each section has one color, so readers know where they are at a glance. |
| Everything clickable | Forms, web pages and contacts open directly. |
| Published view | A clean, read-only viewer with working links; edits appear at the same link. |

It suits reference material that changes occasionally. It suits content that grows every day poorly, because every new page needs its tabs and links maintained.

## 2. Set up the file

1. Create it in the team's shared Drive folder, so it outlives any one person.
2. Name it `<Guide name> (source)`, which marks it as the editable file.
3. **File > Page setup > Custom**, 7.5 x 10 in, before anything else. Changing the size later distorts every page.
4. Optional: start from a free SlidesMania "digital notebook" template, keeping their credit line.
5. Page order: cover (title, "Updated <month year>", logo) → "How to use this guide" (one line) → for each section, a divider and then its content pages → Contacts/Resources.
6. 8 tabs or fewer.

## 3. Build the tabs and links

Build the strip once on a template page, then make every other page by duplicating it.

1. Make the divider pages first. Tabs link to them, so they must exist before you link.
2. Draw one tab: a rounded rectangle about 0.45 in wide and 1.1 in tall, half off the right edge. Rotate the label 90° to read top to bottom; 10-11 pt bold.
3. Copy it down the edge, one per section, in divider order, evenly spaced. Set each label and color.
4. Link each tab: select the shape, press Ctrl/Cmd+K, choose **Slides in this presentation**, and pick the divider. Link the shape, not just the words.
5. Test in **Slideshow**. Links don't respond to a normal click in the editor.
6. Make new pages with **Duplicate slide** from a page in the same section. A blank **New slide** has no tabs.
7. On each section's pages, nudge that section's tab 0.1 in further left so it sticks out.

Don't group the tabs. If someone moves one, copy the strip back from the template page. Putting the tabs on the theme layout (**Slide > Edit theme**) is untested: links there may not click in the published view.

## 4. Color and page layout

- One color per section: its tab, its divider band, and an accent on each of its pages.
- White label text on dark colors, dark text on light ones. Check each pair reaches 4.5:1 (for example with the WebAIM contrast checker).
- Color is never the only signal: tabs and dividers always carry the section name.
- Keep the right 0.6 in of every page empty. Anything covering a tab makes it unclickable.
- Same layout on every content page: title 24-28 pt in the same spot, body at least 14 pt.
- Alt text on every image (right-click > **Alt text**).

## 5. Writing and linking content

- One task per page, titled as the task ("Post an internship", not "Postings").
- Numbered steps for anything done in order; at most about 60 words of prose per page.
- Link descriptive words, never a pasted URL. Link every form, page and email address mentioned.
- Link to the page that does the job, not a site's home page.
- Links within the guide use **Slides in this presentation**, so they survive pages moving.
- Speaker notes are never published; anything readers need goes on the page.
- No calendar dates. Write the lasting rule ("A/B days, 1:00-4:00") and point to where dates are kept (a calendar link, or who to ask). Dates need yearly edits, go stale without anyone noticing, and copies end up disagreeing.

## 6. Publishing

Give readers the **published** link, never the share link to the source.

Why: a share link opens the Slides editor, with menus, a "Request edit access" button and links that pop up instead of opening. The published link opens a clean viewer where tabs work on the first click. Readers don't need a Google account. Only the team can open the source, and speaker notes and comments stay private. Edits appear at the same link.

Steps:
1. **File > Share > Publish to web**.
2. **Link** tab: uncheck **Start slideshow as soon as the player loads** and **Restart the slideshow after the last slide**.
3. **Published content & settings**: check **Automatically republish when changes are made**, if offered.
4. In a school or company Google account, leave any **Restrict access** option unchecked if outside readers need the guide.
5. **Publish**, confirm, and copy the link. It ends in `/pub?start=false&loop=false&delayms=3000`.
6. Open it in a private, signed-out window and click every tab and a sample of links.
7. To place it on a web page, use the **Embed** tab's code.

Anyone with a published link can see the guide, and search engines can find it. Nothing private goes in it. To take it down: **File > Share > Publish to web > Stop publishing**.

## 7. Keeping it current

- One named owner approves changes and owns the published link.
- Edit the source; never publish a copy, which gets a new link and strands everyone who saved the old one.
- Update the cover's "Updated" date with each content change.
- Each cycle (term, season, release), click every tab and link in the published view.
- A new section means a new divider, a new tab on every page and a new color. Keep it rare and within 8 tabs.

## 8. Pre-publish checklist

- [ ] Portrait pages, 7.5 x 10 in
- [ ] 8 tabs or fewer, same order and position on every page
- [ ] Every tab links to its divider (tested in Slideshow)
- [ ] Section colors match across tab, divider and pages
- [ ] Tab labels pass 4.5:1 contrast
- [ ] Nothing covers the tab strip
- [ ] Every form, page and email is a working, descriptive link
- [ ] Images have alt text
- [ ] No private information
- [ ] Cover shows the current "Updated" date
- [ ] Published with autostart and loop off; auto-republish on
- [ ] Published link tested signed out
