# Port Meridian — Gateway to the Other Ocean

A travel poster for a place that isn't there: **Port Meridian**, the harbour
where the sea flows *up* into the sky. A tall ship climbs the vertical
current toward a golden deco sun, above a lamplit quay.

![Port Meridian](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)
![Rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Climaxcuy/visit-port-meridian/rank.svg)
![Reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Climaxcuy/visit-port-meridian/reward.svg)

Built for the make.fun bounty [The poster for a place that isn't there](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539).

## How it works

`main.py` (Python + Pillow, no network) draws the poster — deco blue-and-gold
sky, a golden sun, the vertical ocean current, the climbing tall ship, the
harbour quay — and writes it to `/output/entry.png` (1024×1024, ≤ 1 MiB).
The only text in the picture is the place name itself, set in Playfair
Display Black.

```sh
python3 main.py
```

Fonts ship in `assets/fonts/` (Playfair Display Black, Archivo Bold).
