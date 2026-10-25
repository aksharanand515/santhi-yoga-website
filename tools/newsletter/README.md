# The full moon letter

The newsletter form at the foot of every page sends sign-ups to a Google Sheet
you own, through the Apps Script in `Code.gs`. The same script sends the
letters from your Gmail.

## One-time setup (about 5 minutes)

1. Sign in to Google as **santhiyogacochin@gmail.com**. Letters go out from
   whichever account owns the script.
2. Open <https://sheets.new> and name the sheet `Santhi newsletter`.
3. **Extensions → Apps Script.** Delete what is there, paste all of `Code.gs`,
   and save.
4. **Deploy → New deployment**, gear icon → **Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Press **Deploy**, then **Authorize access**. Google warns that the app is
   unverified because you wrote it yourself: choose **Advanced → Go to
   (project name)** and allow.
6. Copy the **Web app URL** (it ends in `/exec`). Put it in
   `partials/footer.html`, in `data-endpoint=""` on `<form id="nl-form">`,
   then run `node tools/build.js`.

Until step 6 is done the form still works: it opens the visitor's email app
with a request to be added, addressed to santhiyogacochin@gmail.com.

## Sending a letter

1. In Gmail, write the letter as a **draft**. Start the subject with
   `Letter:`, for example `Letter: The November full moon`. The `Letter:` is
   removed before it is sent. Keep only one `Letter:` draft at a time.
   For photos use **Insert photo → Web address (URL)** or attach them; photos
   pasted from your computer will not show.
2. Open the sheet. A **Newsletter** menu appears at the top (reload once if
   not). Choose **Send a test to me** and check it on your phone.
3. Choose **Send the letter to everyone**.

Each letter gets a one-click unsubscribe link at the foot. Gmail allows about
100 recipients a day from a free account; past that, the script stops and
running it again the next day sends to the rest. Column **Last letter** shows
who has had which one.

## If you change `Code.gs`

**Deploy → Manage deployments**, pencil icon, Version **New version**,
**Deploy**. The URL stays the same.
