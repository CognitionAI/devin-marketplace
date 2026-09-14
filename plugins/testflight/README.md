# TestFlight

Ship an iOS/macOS build to TestFlight from a Devin session on a macOS machine
and hand back a public tester link.

The plugin provides the `ship-to-testflight` skill and a `testflight` MCP
server over the App Store Connect API (archive, upload, wait for processing,
"What to Test", beta groups, public links).

## Credentials

Installing the plugin asks for three values, saved as credentials on your
installation and never stored in this repository:

| Credential        | Where it comes from                                                      |
| ----------------- | ------------------------------------------------------------------------ |
| `ASC_ISSUER_ID`   | App Store Connect → Users and Access → Integrations → App Store Connect API |
| `ASC_KEY_ID`      | The Key ID of the API key on that page                                    |
| `ASC_PRIVATE_KEY` | The contents of the `AuthKey_<KEY_ID>.p8` file downloaded when the key was created (base64 of the file also works) |

Create the key with the **App Manager** role: TestFlight uploads, signing asset
generation, and beta group management all need it. Apple lets you download the
`.p8` once — if you no longer have it, revoke the key and create a new one.

The private key is only ever written to disk as a mode-0600 file for
`xcodebuild`/`altool`, and its contents are never returned to the session.
