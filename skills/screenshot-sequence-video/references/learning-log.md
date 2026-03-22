# Learning log

- Durable rule: prefer FFmpeg `image2` only for one contiguous numbered image sequence with uniform image shape/format; otherwise fall back to manifest-driven `concat`.
- Durable rule: for review workflows, sort by `capture_index`, then `frame`, then path instead of plain lexical filename order.
- Durable rule: emit one MP4 per logical sequence plus a JSON sidecar report so later review stages can trace clips back to source images.
- Avoided path: do not silently glue missing-frame or mixed-dimension screenshot sets into a misleading video.