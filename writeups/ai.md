# AI — MODO Prompt Escape

- **Points:** 400
This challenge looked like an AI prompt-escape exercise, but the shortest path was conventional web enumeration. `robots.txt` disclosed `/debug/env`; requesting that endpoint returned a JSON environment snapshot containing the accepted flag under `FLAG_STAGING`.

The neighboring debug endpoint and its RSA-signing hint were unnecessary. In practice, `robots.txt` ended the challenge before prompt injection became relevant.
