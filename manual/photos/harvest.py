"""Collect candidate Commons photos for every posture the manual shows (dev tool)."""
import json
import sys
from pathlib import Path

import commons as C

Q = {
    "sirsasana": ["Sirsasana", "Salamba Sirsasana", "Shirshasana", "yoga headstand"],
    "sarvangasana": ["Sarvangasana", "Salamba Sarvangasana", "shoulderstand yoga"],
    "halasana": ["Halasana", "plough pose yoga", "plow pose yoga"],
    "matsyasana": ["Matsyasana", "fish pose yoga"],
    "paschimottanasana": ["Paschimottanasana", "seated forward bend yoga"],
    "bhujangasana": ["Bhujangasana", "cobra pose yoga"],
    "salabhasana": ["Salabhasana", "Shalabhasana", "locust pose yoga"],
    "dhanurasana": ["Dhanurasana", "bow pose yoga"],
    "ardha_matsyendrasana": ["Ardha Matsyendrasana", "half spinal twist yoga", "Matsyendrasana"],
    "kakasana": ["Kakasana", "crow pose yoga", "Bakasana"],
    "padahastasana": ["Padahastasana", "Uttanasana", "standing forward bend yoga"],
    "trikonasana": ["Trikonasana", "Utthita Trikonasana", "triangle pose yoga"],
    "dolphin": ["dolphin pose yoga", "Ardha Pincha Mayurasana", "Makarasana dolphin"],
    "viparita_karani": ["Viparita Karani", "legs up the wall yoga"],
    "matsyasana_supported": ["supported fish pose", "restorative yoga bolster"],
    "uttana_padasana": ["Uttana Padasana"],
    "sphinx": ["sphinx pose yoga", "Salamba Bhujangasana"],
    "ardha_salabhasana": ["Ardha Salabhasana", "half locust"],
    "easy_twist": ["Parivrtta Sukhasana", "seated twist yoga", "Bharadvajasana"],
    "malasana": ["Malasana", "yoga squat"],
    "mayurasana": ["Mayurasana", "peacock pose yoga"],
    "ardha_uttanasana": ["Ardha Uttanasana", "half forward bend yoga"],
    "pranamasana": ["Pranamasana", "Tadasana Namaste", "Samasthiti yoga"],
    "hasta_uttanasana": ["Hasta Uttanasana", "Urdhva Hastasana"],
    "lunge": ["Ashwa Sanchalanasana", "low lunge yoga", "Anjaneyasana"],
    "plank": ["Phalakasana", "plank pose yoga", "Kumbhakasana"],
    "ashtanga_namaskara": ["Ashtanga Namaskara", "Ashtanga Namaskar"],
    "adho_mukha": ["Adho Mukha Svanasana", "downward dog yoga"],
    "savasana": ["Savasana", "Shavasana", "corpse pose yoga"],
    "meditation": ["Padmasana", "Sukhasana", "lotus position meditation", "Siddhasana"],
    "cat": ["Marjaryasana", "cat pose yoga"],
    "cow": ["Bitilasana", "cow pose yoga"],
    "bridge": ["Setu Bandha Sarvangasana", "bridge pose yoga"],
    "ustrasana": ["Ustrasana", "camel pose yoga"],
    "urdhva_dhanurasana": ["Urdhva Dhanurasana", "Chakrasana yoga wheel"],
    "navasana": ["Navasana", "Paripurna Navasana", "boat pose yoga"],
    "balasana": ["Balasana", "child's pose yoga"],
    "supta_padangusthasana": ["Supta Padangusthasana"],
    "tadasana": ["Tadasana", "mountain pose yoga"],
    "vrksasana": ["Vrksasana", "Vrikshasana", "tree pose yoga"],
    "utkatasana": ["Utkatasana", "chair pose yoga"],
    "virabhadrasana1": ["Virabhadrasana I", "Warrior I yoga"],
    "virabhadrasana2": ["Virabhadrasana II", "Warrior II yoga"],
    "dandasana": ["Dandasana", "staff pose yoga"],
    "vajrasana": ["Vajrasana", "thunderbolt pose yoga"],
    "baddha_konasana": ["Baddha Konasana", "bound angle pose"],
    "leg_raise": ["Uttanpadasana", "supine leg raise yoga", "Urdhva Prasarita Padasana"],
    "sukhasana": ["Sukhasana"],
    "setu": ["Setu Bandhasana"],
}


def main(keys):
    out_dir = C.HERE / "cand"
    out_dir.mkdir(exist_ok=True)
    for key in keys:
        titles = []
        for q in Q[key]:
            titles += C.category("Category:" + q)
            titles += C.search(q, 40)
        titles = [t for t in dict.fromkeys(titles) if t.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"))]
        meta = C.info(titles)
        cands = [m for m in meta.values() if C.free(m) and min(m["w"], m["h"]) >= 700]
        cands.sort(key=lambda m: (-m["usage"], -m["w"] * m["h"]))
        (out_dir / f"{key}.json").write_text(json.dumps(cands, indent=1))
        print(key, len(titles), "->", len(cands), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(Q))
