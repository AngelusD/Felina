# Redesign notes

**Character:** an academic, philosophical practice (Daseinsanalysis) in a warm, lived-in office. Calm and literary rather than playful.

**System (see `:root` in `css/styles.css`):** warm off-white ground · deep teal panels and gradients · aqua fields · blossom-pink accent from the logo (used sparingly) · Roboto throughout · one reading rhythm (16.8 px / 30 px) for all running text · arched and rounded photos in varied silhouettes with a soft colour block behind each.

**Pages:** home (hero collage, portrait, three service columns, gallery, closing band) and six inner pages sharing one split-hero template; side banners for session details; contact page with three action tiles, form and map; privacy notice; 404.

**Motion (reduced-motion safe):** photo reveal, header shrink, gentle parallax, drawn service icons.

**Tooling:** `scripts/build_pages.py` (pages), `optimize_images.py` (photos → WebP/JPEG), `build_dist.py` (upload folder).
