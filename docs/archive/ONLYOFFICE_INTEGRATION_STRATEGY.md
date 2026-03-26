# ONLYOFFICE Integration Strategy

## Goal

Add browser-based document editing and real-time co-authoring to the hybrid platform:

- `NauDoc` as the document workflow/archive/signature contour
- `Rukovoditel` as the user-facing workbench for projects, requests, and document cards
- `middleware` as the synchronization layer

## Key Finding

The practical target is **ONLYOFFICE Docs**, not OpenOffice.

Why:

- `OpenOffice` is a desktop office suite and does not solve embedded browser-based co-authoring.
- `ONLYOFFICE Docs` is the online editor engine designed for embedding into third-party web systems.
- `ONLYOFFICE Workspace` is a whole collaboration platform and overlaps with what `Rukovoditel` is already doing.
- `ONLYOFFICE DocSpace` is useful as a room-based collaboration portal, but it is not the simplest path for the current internal DMS architecture.

## What We Already Have Locally

### NauDoc

`NauDoc` currently has only legacy external editing mechanisms:

- `ExternalEditor`
- `zopeedit`

These are local-editor style integrations, not modern web co-authoring.

Relevant files:

- [ExternalEditor README](/home/lebedeffson/Code/Документооборот/naudoc_project/Products/ExternalEditor/README.txt)
- [zopeedit README](/home/lebedeffson/Code/Документооборот/naudoc_project/zopeedit/README.txt)

### Rukovoditel

`Rukovoditel` already contains a built-in ONLYOFFICE integration layer:

- field type for ONLYOFFICE files
- editor launcher
- download endpoint
- callback handler
- JWT-based config generation

Relevant files:

- [onlyoffice.php](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/includes/classes/onlyoffice/onlyoffice.php)
- [fieldtype_onlyoffice.php](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/includes/classes/fieldstypes/fieldtype_onlyoffice.php)
- [onlyoffice_editor.php](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/modules/items/actions/onlyoffice_editor.php)
- [callback.php](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/modules/onlyoffice/actions/callback.php)
- [download.php](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/modules/onlyoffice/actions/download.php)

Database status:

- table `app_onlyoffice_files` exists
- currently there are no configured `fieldtype_onlyoffice` fields in the process model
- current file count in `app_onlyoffice_files`: `0`

## Important Local Gaps Before Real Use

### 1. Mobile mode is not selected dynamically

The current editor config hardcodes:

- `type = desktop`

File:

- [onlyoffice_editor.php#L46](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/modules/items/actions/onlyoffice_editor.php#L46)

For phones/tablets this should be selected dynamically according to device type or request context.

### 2. Localization config has a bug

The current config sets `lang` twice, so `region` overwrites `lang`:

- [onlyoffice_editor.php#L70](/home/lebedeffson/Code/Документооборот/rukovoditel-test/dist/modules/items/actions/onlyoffice_editor.php#L70)

This should be corrected before rollout.

### 3. ONLYOFFICE is not yet wired into the actual business entities

The process model currently uses document cards and links to `NauDoc`, but not `ONLYOFFICE` file fields yet.

## Product Options

### Option A. ONLYOFFICE Docs inside Rukovoditel

Use `ONLYOFFICE Docs` as the editor engine embedded into `Rukovoditel` entities.

Best fit for:

- internal collaborative drafting
- browser-based editing
- multi-user co-authoring
- mobile-friendly web access, subject to edition/licensing
- keeping current hybrid architecture intact

### Option B. ONLYOFFICE Workspace рядом с системой

This gives mail, docs, projects, CRM, portal features.

Problem:

- it duplicates `Rukovoditel`
- it introduces a second large business portal
- it increases identity, UX and sync complexity

Recommendation:

- **not recommended as the main route** for the current architecture

### Option C. ONLYOFFICE DocSpace as an external collaboration contour

Useful for:

- external rooms
- partner collaboration
- guest access
- isolated co-authoring spaces

Problem:

- room-centric model is not the simplest fit for the current internal DMS workflow
- it adds another top-level collaboration surface

Recommendation:

- consider later for external/extranet scenarios, not as phase 1

## Recommended Architecture

### Recommended target

Use **ONLYOFFICE Docs** as an embedded web editor in `Rukovoditel`.

Keep responsibilities split as follows:

1. `Rukovoditel`
   - create and edit working drafts
   - collaborative editing
   - project/request context
   - user-friendly UI for employees and managers
2. `middleware`
   - synchronize metadata, statuses and links
   - trigger export/publication to `NauDoc`
   - later manage version handoff rules
3. `NauDoc`
   - official document card
   - registration
   - approval route
   - archive
   - digital signature / legal contour

### Practical flow

1. User creates a request/project/document card in `Rukovoditel`.
2. A draft file is attached through an `ONLYOFFICE` field.
3. Several users edit the same file in the web editor.
4. When the draft is ready, the document card is pushed into `NauDoc`.
5. `NauDoc` remains the official registration / approval / signature contour.
6. `middleware` stores the relationship between:
   - request/project
   - draft file
   - document card
   - final `NauDoc` URL and status

### Soft NauDoc integration

If users must start from `NauDoc`, we do not need to embed the whole editor into legacy Zope pages first.

Safer phase-1 approach:

1. keep the authoritative document card in `NauDoc`
2. store the linked `Rukovoditel` draft / editor record in `middleware`
3. add an action in `NauDoc`, for example `Open draft in ONLYOFFICE`
4. route the user to the linked `Rukovoditel + ONLYOFFICE` editor session

This gives an “inside the system” feel without forcing the riskiest deep legacy integration first.

## Why This Is Better Than Embedding ONLYOFFICE Directly Into NauDoc First

Because `NauDoc` is the oldest and riskiest place to build new UI behavior.

Direct integration into `NauDoc` would require:

- custom web embedding in legacy Zope pages
- custom download/callback endpoints in old Python/Zope code
- new permission mapping in the legacy document objects
- more fragile maintenance

By contrast, `Rukovoditel` already has a ready integration layer and modern-ish entity model for user work.

## Linux And Mobile Reality

For a Linux-hosted platform, `ONLYOFFICE Docs` is a natural fit because it is deployed on Linux and exposed in the browser.

But there is an important licensing nuance:

- web co-authoring in browser is supported by `ONLYOFFICE Docs`
- **mobile web editors are officially available only for commercial builds of ONLYOFFICE Docs (`Enterprise` / `Developer`)**
- if using Community-oriented builds, do not assume full mobile editing parity without verification against the chosen edition

So if mobile editing is a hard requirement, we should treat commercial ONLYOFFICE Docs as the realistic target.

## Infrastructure Notes

`ONLYOFFICE Docs` must be reachable both:

1. from end-user browsers
2. from the host application that provides document URLs and receives save callbacks

In our architecture that means:

1. `Rukovoditel` must be able to serve file download URLs to `ONLYOFFICE Docs`
2. `ONLYOFFICE Docs` must be able to call back into `Rukovoditel`
3. JWT secret must match on both sides
4. public URLs behind the gateway must be stable

## Exact Recommendation For Our Platform

### Phase 1. Drafting in Rukovoditel

1. Add `ONLYOFFICE` fields to:
   - document cards
   - selected request entities
   - selected project entities
2. Configure `ONLYOFFICE Docs` server URL and JWT secret.
3. Fix the local integration issues:
   - dynamic `desktop/mobile/embedded` selection
   - `lang/region` config bug
4. Enable edit permissions only for the proper roles / assigned users.

### Phase 2. Controlled publication into NauDoc

1. Define which file becomes the official publishable version.
2. Add middleware rules for:
   - draft status
   - ready for registration
   - registered in `NauDoc`
   - approved/signed/archived
3. Store final `NauDoc` URL back in `Rukovoditel`.

### Phase 3. Better UX

1. Add “Open in ONLYOFFICE” action directly in cards.
2. Show draft/final distinction in lists and dashboards.
3. Add manager view:
   - who is editing now
   - last modified by
   - draft readiness vs official approval status

## What I Recommend We Do Next

### Minimal realistic implementation path

1. Deploy a standalone `ONLYOFFICE Docs` container next to the current stack.
2. Add one pilot `fieldtype_onlyoffice` field to `Карточки документов` in `Rukovoditel`.
3. Fix the two local integration issues.
4. Run one end-to-end scenario:
   - create draft
   - co-edit from two browsers
   - save callback
   - link to `NauDoc` card
5. Then extend to requests/projects.

## Final Conclusion

The fastest and safest path is:

- **do not add OpenOffice**
- **do not make ONLYOFFICE Workspace the second main portal**
- **use ONLYOFFICE Docs as the embedded collaborative editor inside Rukovoditel**
- **keep NauDoc as the official workflow/archive/signature system**
- **use middleware to synchronize the drafting contour with the formal document contour**

That gives us:

- web editing
- multi-user co-authoring
- a better Linux-friendly deployment path
- a realistic mobile path
- minimal disruption to the system we already assembled
