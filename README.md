# The World Today — 24 November 2026

make.fun `news-image-20261124` entry: a one-page newspaper front page summing
up the world news of Tuesday 24 November 2026, drawn 100% from code.

`main.py` (Python 3 stdlib only, no network) renders a 1024x1024 PNG with a
built-in 5x7 bitmap font and a hand-rolled PNG encoder. Lead story: Jensen
Huang returns as Nvidia CEO (+31%, nearly $1 trillion added). Also: Indonesia
factory fire (24 dead), Russian corvette destroyed at Benghazi, COP31 ends
without a deal, Kyiv-region strike, India–Nepal pact, Bangladesh Hasina
arrest vow, plus FIFA World Cup hosts, India–NZ Test, O'Hare ground stop,
China welfare targets and South Korea reshuffle.

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py` — writes `out/entry.png`.
Deterministic: two runs produce byte-identical output (sha256
`093104bbf70d53c0e82f67e9d8c2e9ffa9c3964df34b87cc4da29eb60007088a`).
