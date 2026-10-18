# Unity CLI Personal-license investigation — synthetic cloud runner

**Scope:** Credential-free, isolated public GitHub Actions CI; BEACON production code/assets untouched. Existing `unity-proof.yml` remains disabled until the owner explicitly approves a supported, secure Unity Personal license activation route. Do not set `ENABLE_UNITY_POC` solely because this discovery passes.

**Known facts from vendor sources (2026-10-17):**
- Unity's new experimental CLI supports headless Ubuntu installation and project test/build tooling, but those actions require an activated Editor license.
- Unity's own [CLI licensing reference](https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/references/auth-license-cloud.md) documents `unity license activate --personal --accept-eula` **only after sign-in by a human Unity account**. It explicitly says Unity **service account tokens do not activate Personal licenses**.
- `unity auth login` opens an interactive browser authorization. No unattended human-user refresh-token injection, stored cookie export or MFA workaround is authorized. Unity's conventional Editor licensing docs also say Personal is managed through Hub; the experimental CLI's newer Personal option needs **actual** validation before production adoption.
- GameCI's current workflow expects a `.ulf` plus protected Unity account secrets, but the owner has only `UnityEntitlementLicense.xml` on their local machine. Do not rename, publish or transmit that license or account credentials.

**Safe experiment:** On push/main, Ubuntu runner installs the CLI from Unity's **signed vendor apt repository**, reads `--version`/`--help`, checks that `--personal` and `--accept-eula` are offered, runs synthetic safety/tests, and uploads a receipt. It **does not** sign in, attempt activation, install an Editor, perform Unity C# tests or build a Windows executable. Neither the GitHub runner nor the owner PC receives account information from this experiment. Expire receipt artifact after one day.

**Success means only:** official CLI package works on a GitHub-hosted Ubuntu environment, with command-line licensing interface available and no credentials. It **does not** establish unattended Personal activation or real Unity compilation. If experimental flags differ, capture mismatch and stop without weakening policy or revealing secrets.

**Next blocked dependency:** To progress to actual cloud Unity Editor activation, independently establish a vendor-supported user authentication/session method appropriate to a disposable runner **without** unsafe persistence or repeated owner intervention. If not possible for Personal, mark remote CI license BLOCKED, maintain protected disabled job, and consider a supported alternative only with the owner's consent. Any future permission or EULA approval belongs to the owner. Production HR-010 gameplay/Unity freeze unchanged.

**Sources:** [Official Unity CLI install guide](https://docs.unity.com/en-us/unity-cli/use-unity-cli); [Unity's maintained CLI licensing reference](https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/references/auth-license-cloud.md); [Unity license activation docs](https://docs.unity.com/en-us/engine/6000.0/manual/get-started/install-and-upgrade/licenses-and-activation/license-activation-methods); [GameCI activation](https://game.ci/docs/github/activation/).
