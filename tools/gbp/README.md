# Google Business Profile

`review-replies.json` holds the owner's reply for every Google review, written in
the school's voice. `posted: true` marks the ones already published, so a reply is
never sent twice. The replies are published through the Windsor.ai Google Business
Profile connector, one `reply_to_review` call per review.

`service-items.json` is the full list of services shown on the profile. The
connector's `update_service_items` call replaces the whole list, so change this
file and send every item in it, never just the new one.

Where a reviewer's display name was initials, a username, or a name that could be
mistaken for a teacher's, the reply opens with a plain "Thank you so much" and no name.
