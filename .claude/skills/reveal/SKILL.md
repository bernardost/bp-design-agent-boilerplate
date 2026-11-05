---
name: reveal
description: Show a file or folder in Finder with it selected, so the owner can drag, attach or open it himself. Use for /reveal, "show me where it is", "reveal in Finder", "where's that file".
---

# Reveal

Run:

```
python3 brain/show.py --reveal <path> [more…]
```

- **What to reveal.** The argument he gave. With no argument, the file the conversation is
  about: the last one you wrote or named for him.
- **Say the path in the reply**, one line.

If the script prints that there is no screen (a remote session), say so in one line and give
the path.
