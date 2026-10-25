/**
 * Santhi School of Yoga — the full moon letter
 *
 * A Google Apps Script that lives inside a Google Sheet. It
 *   • takes sign-ups from the website form (doPost) into the "Subscribers" tab,
 *   • sends each new subscriber a short welcome from this Gmail account,
 *   • unsubscribes people from the link at the foot of every letter (doGet),
 *   • sends a letter you wrote as a Gmail draft to everyone subscribed
 *     (the Newsletter menu at the top of the sheet).
 *
 * Setup steps are in README.md beside this file.
 */

var SHEET = 'Subscribers';
var FROM_NAME = 'Santhi School of Yoga & Vedanta Studies';
var SITE = 'https://santhiyogaindia.com/';
// a Gmail draft whose subject starts with this is the letter to send; the tag is dropped when sending
var TAG = 'Letter:';
var HEAD = ['Joined', 'Email', 'Name', 'Page', 'Status', 'Token', 'Last letter'];
var COL = { email: 2, status: 5, token: 6, last: 7 };

/* ---------- Sheet ---------- */
function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEAD);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEAD.length).setFontWeight('bold');
  }
  return sh;
}
// a name like "=HYPERLINK(...)" would otherwise run as a formula in the sheet
function cell_(s, max) {
  s = String(s || '').trim().slice(0, max);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}
function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function unsubUrl_(token) { return ScriptApp.getService().getUrl() + '?u=' + encodeURIComponent(token); }

/* ---------- Sign-up from the website ---------- */
function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.website) return json_({ ok: true }); // the hidden field only bots fill in
  var email = String(p.email || '').trim().toLowerCase();
  if (email.length > 120 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json_({ ok: false, error: 'email' });
  var name = cell_(p.name, 60), token;

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sh = sheet_(), rows = sh.getDataRange().getValues();
    for (var i = 1; i < rows.length; i++) {
      if (String(rows[i][COL.email - 1]).toLowerCase() === email) {
        if (rows[i][COL.status - 1] !== 'subscribed') sh.getRange(i + 1, COL.status).setValue('subscribed');
        return json_({ ok: true, existing: true });
      }
    }
    token = Utilities.getUuid();
    sh.appendRow([new Date(), email, name, cell_(p.page, 120), 'subscribed', token, '']);
  } finally {
    lock.releaseLock();
  }
  welcome_(email, name.replace(/^'/, ''), token);
  return json_({ ok: true });
}

function welcome_(email, name, token) {
  var hello = name ? 'Dear ' + name + ',' : 'Hello,';
  var html =
    '<div style="font:17px/1.7 Georgia,serif;color:#2D2A1F;max-width:560px">' +
    '<p>' + hello + '</p>' +
    '<p>Thank you for asking us to write. Once a month, as the moon comes full over Fort Kochi, we send a letter from the shala: ' +
    'a practice to try at home, a few lines from the old texts, how the season feels in Kerala, and the dates of our next training and retreat.</p>' +
    '<p>If you have a question about your practice, just reply to this email. It comes straight to us.</p>' +
    '<p>From the shala,<br>Santhi School of Yoga &amp; Vedanta Studies<br>Fort Kochi, Kerala</p>' +
    '<p style="font:12px/1.6 Arial,sans-serif;color:#8a8270;margin-top:32px">' +
    '<a href="' + SITE + '" style="color:#7A5A1E">santhiyogaindia.com</a> · ' +
    '<a href="' + unsubUrl_(token) + '" style="color:#8a8270">Stop these letters</a></p></div>';
  var plain = hello + '\n\nThank you for asking us to write. Once a month, on the full moon, we send a letter from the shala in Fort Kochi.\n\n' +
    'From the shala,\nSanthi School of Yoga & Vedanta Studies\n\nStop these letters: ' + unsubUrl_(token);
  GmailApp.sendEmail(email, 'Your first note from Fort Kochi', plain, { htmlBody: html, name: FROM_NAME });
}

/* ---------- Unsubscribe link ---------- */
function doGet(e) {
  var token = (e && e.parameter && e.parameter.u) || '', found = false;
  if (token) {
    var sh = sheet_(), rows = sh.getDataRange().getValues();
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][COL.token - 1] === token) {
        sh.getRange(i + 1, COL.status).setValue('unsubscribed');
        found = true;
        break;
      }
    }
  }
  var msg = found
    ? 'You will not receive any more letters from us. Thank you for reading them, and you are always welcome back in Fort Kochi.'
    : 'This link has already been used or is not valid. If letters still arrive, reply to one and we will take you off by hand.';
  return HtmlService.createHtmlOutput(
    '<div style="font:20px/1.7 Georgia,serif;color:#2D2A1F;max-width:520px;margin:12vh auto;padding:0 20px;text-align:center">' +
    '<p style="font-size:30px;margin:0 0 12px">Namaste</p><p>' + msg + '</p>' +
    '<p style="font:14px Arial,sans-serif"><a href="' + SITE + '" style="color:#7A5A1E">santhiyogaindia.com</a></p></div>'
  ).setTitle('Santhi School of Yoga').addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/* ---------- Sending a letter ---------- */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('Newsletter')
    .addItem('Send a test to me', 'sendTest')
    .addItem('Send the letter to everyone', 'sendLetter')
    .addToUi();
}

function draft_() {
  var drafts = GmailApp.getDrafts().filter(function (d) { return d.getMessage().getSubject().indexOf(TAG) === 0; });
  if (!drafts.length) throw new Error('No Gmail draft found with a subject starting "' + TAG + '". Write the letter in Gmail as a draft first.');
  return drafts[0].getMessage();
}

function compose_(msg, token) {
  var url = unsubUrl_(token);
  return {
    subject: msg.getSubject().slice(TAG.length).trim(),
    plain: msg.getPlainBody() + '\n\n--\nSanthi School of Yoga & Vedanta Studies, Fort Kochi\nStop these letters: ' + url,
    options: {
      name: FROM_NAME,
      attachments: msg.getAttachments({ includeInlineImages: false }),
      htmlBody: msg.getBody() +
        '<p style="font:12px/1.6 Arial,sans-serif;color:#8a8270;margin-top:36px;border-top:1px solid #eadfcd;padding-top:14px">' +
        'Santhi School of Yoga &amp; Vedanta Studies · Fort Kochi, Kerala · ' +
        '<a href="' + SITE + '" style="color:#7A5A1E">santhiyogaindia.com</a><br>' +
        'You asked for these letters on our website. <a href="' + url + '" style="color:#8a8270">Stop them with one click</a>.</p>'
    }
  };
}

function sendTest() {
  var me = Session.getEffectiveUser().getEmail(), m = compose_(draft_(), 'test');
  GmailApp.sendEmail(me, '[Test] ' + m.subject, m.plain, m.options);
  SpreadsheetApp.getUi().alert('A test of "' + m.subject + '" is on its way to ' + me + '.');
}

// Sends the draft to everyone subscribed who has not had it yet. Gmail allows about
// 100 recipients a day from a free account: when the quota runs out it stops, and
// running it again the next day carries on from where it stopped.
function sendLetter() {
  var ui = SpreadsheetApp.getUi(), msg = draft_(), subject = compose_(msg, '').subject;
  var sh = sheet_(), rows = sh.getDataRange().getValues(), todo = [];
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][COL.status - 1] === 'subscribed' && rows[i][COL.last - 1] !== subject) todo.push(i);
  }
  if (!todo.length) { ui.alert('Everyone subscribed already has "' + subject + '".'); return; }
  var quota = MailApp.getRemainingDailyQuota();
  var ok = ui.alert('Send "' + subject + '"?', todo.length + ' people will get it. Gmail lets you send ' + quota + ' more today.', ui.ButtonSet.OK_CANCEL);
  if (ok !== ui.Button.OK) return;

  var sent = 0;
  for (var j = 0; j < todo.length && MailApp.getRemainingDailyQuota() > 0; j++) {
    var r = todo[j], m = compose_(msg, rows[r][COL.token - 1]);
    GmailApp.sendEmail(rows[r][COL.email - 1], m.subject, m.plain, m.options);
    sh.getRange(r + 1, COL.last).setValue(subject);
    sent++;
  }
  var left = todo.length - sent;
  ui.alert(left ? 'Sent to ' + sent + '. Gmail’s daily limit is reached: run it again tomorrow for the other ' + left + '.' : 'Sent to all ' + sent + '.');
}
