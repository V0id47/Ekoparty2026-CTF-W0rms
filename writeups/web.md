# Web

## Certificate Exchange by Kulkan Security

- **Points:** 200
The HTTPS service expected a client certificate. A first exchange returned a Base64 blob encrypted with repeating-key XOR. A known PEM prefix exposed the 25-byte key `OMG_I_LUV_EKO_ARG_XOR_KEY`; decrypting the blob recovered a second certificate and its private key.

The recovered certificate had subject `O=Kulkan, CN=level-2.exchange.kulkan.local` and was issued by `Kulkan Root CA`. Repeating the exchange with that certificate completed mutual TLS and returned the flag.

## My Notes

- **Points:** 200
The note previewer fetched URLs server-side. It blocked internal destinations on the initial URL, but did not revalidate the destination after following an external redirect.

The chain I used was:

1. Create a note containing an allowed external URL that redirects to `internal-swagger:8080/openapi.json`.
2. Read the internal OpenAPI document from the preview response. It disclosed `cache-service:8080` and `vault-service:8080`.
3. Follow another redirect to the cache. An unauthenticated vault request disclosed the reserved credential name `secret:vault:m2m`.
4. Fetch that exact cache key through SSRF.
5. Pass the recovered value through the documented `api_key` query parameter to the vault service and retrieve the flag.

The transient M2M credential and all internal addresses were removed from this publication.

The bug was in redirect handling: the first URL passed validation, while the destination reached after the redirect did not go through the same checks. The internal OpenAPI document supplied the rest of the route.
