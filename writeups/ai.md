# AI — MODO Prompt Escape

- **Points:** 400
- **Flag:** `HIK_NAO_ADIANTA_USAR_IA_HAHAHA_54648618C8784494979787979`

This challenge looked like an AI prompt-escape exercise, but the shortest path was conventional web enumeration. `robots.txt` disclosed `/debug/env`; requesting that endpoint returned a JSON environment snapshot containing the accepted flag under `FLAG_STAGING`.

The neighboring debug endpoint and its RSA-signing hint were unnecessary. The important lesson was to enumerate the surrounding application before spending time attacking the conversational surface.
