#!/usr/bin/env python3
"""Santhi School of Yoga & Vedanta Studies: move the site to the November 2026 prices.

From 1 November 2026 a drop-in class is ₹700 (it was ₹500, an introductory
price on the usual ₹600) and a private session is ₹2,000 (it was ₹1,500).
Until then the site gives both prices side by side; this states the new ones
plainly and drops the "limited-time" and "from November 2026" wording.
Other people's prices (studios, tourist platforms, taxis, massages) are
left alone.

It also reworks the monthly budget in blog/cost-of-a-month-in-fort-kochi:
24 classes a month with the 30% long-stay discount is 24 x 490 = 11,760,
about 12,000; with the first week at full price, 6 x 700 + 18 x 490 =
13,020, about 13,000; the comfortable column adds two private sessions,
13,000 + 4,000 = 17,000. And it moves the "Updated" date of every page it
changes to 1 November 2026.

Usage:
  python3 tools/november-prices.py           apply the changes
  python3 tools/november-prices.py --check   list what would change, write nothing
Then run: node tools/build.js
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE_ISO, DATE_TEXT = '2026-11-01', '1 November 2026'

# (pattern, replacement): regular expressions, applied to every source file
RULES = [
    # Drop-in class
    (r'₹500( a class| for two hours| each)? \(a limited-time offer; normally ₹600, and ₹700 from November 2026\)', r'₹700\1'),
    (r'₹500( a class| for two hours| for 2 hours| each)? \((?:offer; )?normally ₹600\)', r'₹700\1'),
    (r'₹500 a class — a limited-time offer on the usual ₹600, and ₹700 from November 2026', '₹700 a class'),
    (r'₹500 at present, a limited-time offer on the usual ₹600, rising to ₹700 in November 2026', '₹700'),
    (r'<strong>₹500 at the moment</strong>, a limited-time offer on the usual ₹600, and it becomes ₹700 from November 2026', '<strong>₹700</strong>'),
    (r'₹500 at the moment\.</strong> That is a limited-time offer on the usual ₹600, and from November 2026 the class will be ₹700\.', '₹700.</strong>'),
    (r'₹500 per class \(offer; normally ₹600\) · ₹700 from Nov 2026 · ', '₹700 per class · '),
    (r' A limited-time price; normally ₹600, and ₹700 from November 2026\.', ''),
    (r'₹500 at present — a limited-time offer on the usual ₹600\. From November 2026 the class is ₹700\.', '₹700.'),
    (r'<dt>A class</dt><dd>₹500</dd>', '<dt>A class</dt><dd>₹700</dd>'),
    (r'at 7:30 am and 3:30 pm\. ₹500 a class\.', 'at 7:30 am and 3:30 pm. ₹700 a class.'),
    (r'<td>Our drop-in class, two hours</td><td>₹500</td><td><strong>₹250</strong></td>',
     '<td>Our drop-in class, two hours</td><td>₹700</td><td><strong>₹350</strong></td>'),
    # Private session
    (r'₹1,500( a session)?, rising to ₹2,000 in November 2026', r'₹2,000\1'),
    (r'₹1,500 \(₹2,000 from Nov(?:ember)? 2026\)', '₹2,000'),
    (r'₹1,500, rising to ₹2,000\.', '₹2,000.'),
    (r'<strong>₹1,500 a session</strong>, rising to <strong>₹2,000 in November 2026</strong>', '<strong>₹2,000 a session</strong>'),
    (r'goals and pace\. ₹2,000 from November 2026\.', 'goals and pace.'),
    # The home page's structured data
    (r'"priceRange": "₹500–₹1,500"', '"priceRange": "₹700–₹2,000"'),
    (r'"price": "500",', '"price": "700",'),
    (r'"price": "1500",', '"price": "2000",'),
    # The monthly budget
    (r'₹8,000–10,000 — call it €85–105', '₹12,000–13,000 — call it €125–140'),
    (r'works out at roughly ₹8,000–10,000\.', 'works out at roughly ₹12,000–13,000.'),
    (r'<td>Yoga, six days a week</td><td>8,500</td><td>10,000</td><td>13,000</td>',
     '<td>Yoga, six days a week</td><td>12,000</td><td>13,000</td><td>17,000</td>'),
    (r'<strong>≈ 38,000</strong></td><td><strong>≈ 64,000</strong></td><td><strong>≈ 102,000</strong>',
     '<strong>≈ 41,500</strong></td><td><strong>≈ 67,000</strong></td><td><strong>≈ 106,000</strong>'),
]

# Wording that must be gone afterwards; (pattern, allowed-context pattern or None)
LEFTOVERS = [
    (r'November 2026|Nov 2026', r'datetime="2026-11-01">1 November 2026$'),
    (r'limited-time', None),
    (r'normally ₹600|usual ₹600', None),
    (r'₹500', None),
    (r'₹1,500', r'Ayurvedic massage or treatment.{0,50}₹1,500'),
]

SOURCES = [p for p in ROOT.rglob('*') if p.suffix in {'.html', '.md', '.js'}
           and 'node_modules' not in p.parts and p.name not in {'site.min.js'}
           and not p.is_relative_to(ROOT / 'tools')]


def main():
    check = '--check' in sys.argv
    total, changed = 0, []
    for path in sorted(SOURCES):
        text = path.read_text(encoding='utf-8')
        new, count = text, 0
        for pattern, repl in RULES:
            new, n = re.subn(pattern, repl, new)
            count += n
        if not count:
            continue
        # a changed page is an updated page
        new = re.sub(r'"dateModified": "\d{4}-\d{2}-\d{2}"', f'"dateModified": "{DATE_ISO}"', new)
        new = re.sub(r'Updated <time datetime="\d{4}-\d{2}-\d{2}">[^<]*</time>',
                     f'Updated <time datetime="{DATE_ISO}">{DATE_TEXT}</time>', new)
        total += count
        changed.append(path)
        print(f'{count:3}  {path.relative_to(ROOT)}')
        if not check:
            path.write_text(new, encoding='utf-8')
    print(f'{total} changes in {len(changed)} files' + (' (check only, nothing written)' if check else ''))
    if check:
        return

    problems = []
    for path in sorted(SOURCES):
        text = path.read_text(encoding='utf-8')
        for pattern, allowed in LEFTOVERS:
            for m in re.finditer(pattern, text):
                window = text[max(0, m.start() - 60):m.end() + 5]
                if allowed and re.search(allowed, text[max(0, m.start() - 60):m.end()], re.S):
                    continue
                problems.append(f'{path.relative_to(ROOT)}: …{window.strip()[-90:]}')
    if problems:
        print('\nStill mentions an old price; fix by hand:')
        print('\n'.join(problems))
        sys.exit(1)
    print('No old prices left.')


if __name__ == '__main__':
    main()
