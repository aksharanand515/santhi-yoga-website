"""
Wikimedia Commons helper for the manual's posture photographs.

Only freely licensed files are accepted (CC0, public domain, CC BY, CC BY-SA); every photo used
in the book is credited on the photo-credits page generated from photos/credits.json.
"""
import json
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = "SanthiYogaManualBuilder/1.0 (https://github.com/aksharanand515/santhi-yoga-website; manual illustrations)"
HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
OK_LICENSES = ("cc0", "public domain", "pd", "cc by", "cc-by", "cc by-sa", "cc-by-sa")


_last = [0.0]


def _pace(gap=1.0):
    """Keep at least `gap` seconds between requests (Wikimedia API etiquette)."""
    wait = _last[0] + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()


def get(params, tries=8):
    params = dict(params, format="json", formatversion=2, maxlag=5)
    url = API + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        _pace()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            ra = e.headers.get("retry-after")
            time.sleep(float(ra) if ra and ra.isdigit() else min(60, 3 * 2 ** k))
        except Exception:
            time.sleep(min(60, 3 * 2 ** k))
    raise RuntimeError(url)


def search(query, limit=50):
    d = get(dict(action="query", list="search", srsearch=query, srnamespace=6, srlimit=limit))
    return [x["title"] for x in d.get("query", {}).get("search", [])]


def category(cat, limit=200):
    d = get(dict(action="query", list="categorymembers", cmtitle=cat, cmtype="file", cmlimit=limit))
    return [x["title"] for x in d.get("query", {}).get("categorymembers", [])]


def info(titles, thumb=400):
    """imageinfo + licence metadata + global usage count for up to 50 titles."""
    out = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        d = get(dict(action="query", titles="|".join(chunk), prop="imageinfo|globalusage",
                     iiprop="url|size|mime|extmetadata", iiurlwidth=thumb, gulimit=500))
        for p in d.get("query", {}).get("pages", []):
            if "imageinfo" not in p:
                continue
            ii = p["imageinfo"][0]
            em = ii.get("extmetadata", {})
            val = lambda k: (em.get(k, {}) or {}).get("value", "")  # noqa: E731
            out[p["title"]] = dict(
                title=p["title"], url=ii["url"], thumb=ii.get("thumburl"), w=ii["width"], h=ii["height"],
                mime=ii["mime"], license=val("LicenseShortName"), license_url=val("LicenseUrl"),
                artist=val("Artist"), credit=val("Credit"), desc=val("ImageDescription"),
                usage=len(p.get("globalusage", [])),
                page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")))
    return out


def free(meta):
    lic = meta["license"].lower()
    return any(lic.startswith(x) for x in OK_LICENSES) and "nc" not in lic and "nd" not in lic


def _host(url):
    """thumb.wikimedia.org is not reachable from the build environment; upload.wikimedia.org
    serves the same thumbnails."""
    return url.replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/").split("?")[0]


def sized(meta, width):
    """URL of a standard-width thumbnail (Wikimedia serves 500, 960, 1280, 1920 …)."""
    t = meta["thumb"]
    import re
    return re.sub(r"/\d+px-", f"/{width}px-", t)


def download(url, dest, tries=20):
    url = _host(url)
    dest = Path(dest)
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for k in range(tries):
        _pace(2.0)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                dest.write_bytes(r.read())
            return dest
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                raise
            ra = e.headers.get("retry-after")
            wait = min(float(ra), 120) if ra and ra.isdigit() else min(90, 10 * 2 ** k)
            print(f"  429, waiting {wait:.0f}s", flush=True)
            time.sleep(wait)
        except Exception:
            time.sleep(min(90, 10 * 2 ** k))
    raise RuntimeError(url)
