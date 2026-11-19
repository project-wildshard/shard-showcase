# Wildshard Art Workshop

This is the separate website checkout for the Wildshard Art Workshop, not the game. It contains the complete static website: the concept and asset catalog, Blender gallery, original reference gallery, and their web media.

## Run locally

```sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000. No build, API key, game assets, or services are required for the site itself. Links to the original historical sources are external.

This branch is a standalone website snapshot. Game model exports belong on `art`. Nothing from this branch needs to be merged into `main`.
