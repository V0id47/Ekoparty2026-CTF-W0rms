# ZM.js

- **Category:** Binary Exploitation
- **Points:** 400

The service was an HTTP image API backed by QuickJS-ng. Every TCP connection owned an independent native session, so the complete exploit had to remain on one keep-alive connection.

## Vulnerability

The recent-images list retained a native object after its image was deleted. A controlled allocation sequence produced a dangling entry:

1. Create a small guard image.
2. Create an `8×8` image and its thumbnail.
3. Delete the original image.
4. Trigger a metadata allocation that reuses the freed native chunk.
5. Read the dangling recent entry through `/api/recent/0/data`.

The leak contained a libc pointer to `free`. Subtracting its known offset yielded the libc base and therefore the address of `system`.

## Exploitation

A second metadata allocation reclaimed the relevant chunk. The recent-entry patch endpoint then replaced the function pointer with `system`. Supplying a command string as the object argument turned the next cleanup into command execution.

The HTTP socket was file descriptor 4 in the worker. The final command was equivalent to:

```sh
cat<flag.txt>&4;#
```

Writing to the existing socket placed the flag immediately before the service's normal HTTP error response.

The exploitable state lived below JavaScript: `/api/recent` kept a native pointer after deletion, and the debug patch endpoint made the reclaimed object writable. Keeping the whole sequence on one HTTP connection was the detail that made the exploit reliable.
