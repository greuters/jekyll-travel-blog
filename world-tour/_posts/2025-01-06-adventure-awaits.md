---
layout: post
lang: en
title: Starting off your journey
preview_image_id: gallery/avontuur.jpg
preview_text: |
  This is how your world tour might start.. documented in a dedicated blog.
track_number: 1
spread_direction: "SE"
image_metadata:
  - dirname:
    images:
      - {filename: "solar-bike-night.jpg", caption: "Solar bike in the desert night", alt: ""}

  - dirname: gallery
    images:
      - {filename: "abendstimmung.jpg", caption: "", alt: "Sunset on the Atlantic"}
      - {filename: "gischt.jpg", caption: "Rough seas", alt: ""}
      - {filename: "avontuur.jpg", caption: "Avontuur - sailing cargo like in the old days", alt: ""}
---

## Banners ..

Your posts might contain single images used as a same-height **image-divider**:

{% include image-divider.html ids="solar-bike-night.jpg, gallery/avontuur.jpg, gallery/gischt.jpg" %}

## .. floating images ..

in different **float layouts** next to text:

<div class="flow-root">
  {% include image.liquid id="gallery/abendstimmung.jpg" class="float-inline-start"%}

  Prow scuttle parrel provost Sail ho shrouds spirits boom mizzenmast yardarm.
  Pinnace holystone mizzenmast quarter crow's nest nipperkin grog yardarm
  hempen halter furl. Swab barque interloper chantey doubloon starboard grog
  black jack gangway rutters.
</div>

{% include image.liquid id="gallery/avontuur.jpg" class="float-inline-end"%}

Trysail Sail ho Corsair red ensign hulk smartly boom jib rum gangway. Case shot
Shiver me timbers gangplank crack Jennys tea cup ballast Blimey lee snow crow's
nest rutters. Fluke jib scourge of the seven seas boatswain schooner gaff booty
Jack Tar transom spirits.

<div class="float-clear"></div>

<div class="flow-root">
  {% include image.liquid id="solar-bike-night.jpg" class="centered"%}

  Deadlights jack lad schooner scallywag dance the hempen jig carouser
  broadside cable strike colors. Bring a spring upon her cable holystone blow
  the man down spanker Shiver me timbers to go on account lookout wherry
  doubloon chase. Belay yo-ho-ho keelhaul squiffy black spot yardarm spyglass
  sheet transom heave to.
</div>

## .. and galleries

or as an **animated gallery**

{% include inline-gallery.html collection="gallery" %}
