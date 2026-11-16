# VEIL private evidence review pilot

This is a local operator workflow for an invited, no-fee case. It uses Python 3.10+ and, for SIGNAL CSV analysis, Node.js. It starts no network listener. Run the [synthetic regression suite](../../tools/evidence-review/test_pilot.py) before handling a consented case. Use synthetic evidence until the operator has tested the workstation, storage access, private handoff, and backup restoration.

## Prepare the workstation and consent

- Use a dedicated private directory on an encrypted local volume outside every repository checkout, website root, shared drive, and sync folder. On Linux/macOS the directory must be owner-only (0700); the pilot checks existing database ownership and permissions there. On Windows, set and verify owner-only access with Windows ACLs, and confirm encryption under the local OS account before using real data. Use a private terminal. Keep evidence, consent records, keys, backups, and reports off GitHub.
- Agree on the question, file limits, authorized participants, retention date, and private report delivery. Confirm who owns the files and has authority to share them. Retain a private consent record and use only an opaque reference in this tool. The pilot has no permission for publication or model training.
- Use a private, verified handoff. Record the transfer date and expected SHA-256 from a channel where you have verified the submitter. The checksum verifies the received bytes. The submitter and operator document source, device, time zone, clock uncertainty, and acquisition context separately.
- Keep sensitive notes out of shell history and process arguments. Supply them from a trusted local argument file using `@path-to-file`, one argument per line with no shell quoting. Restrict permissions and retain or delete the argument file under the same case retention plan. Never use a submitter-supplied argument file.

## Encrypted handoff rehearsal

OpenSSL 3 is an optional offline transfer tool. Before using it, the operator provisions a dedicated recipient certificate and password-protected private key. The operator shares only the public certificate. Confirm its full SHA-256 fingerprint over an independently verified channel. Rehearse with a short-lived synthetic certificate and original.

```text
openssl x509 -in recipient.pem -noout -sha256 -fingerprint
openssl cms -encrypt -binary -aes-256-gcm -in original.csv -outform DER -out case-file.cms recipient.pem
openssl cms -decrypt -binary -inform DER -in case-file.cms -recip recipient.pem -inkey recipient.key -out received.csv
```

The submitter transfers the encrypted file through the agreed private channel and retains their original. The operator decrypts to a new path on the protected volume. Discard any output from a failed decrypt and match the submitter's digest at intake. Keep the private key and passphrase separate from the transferred files. The encryption authenticates the encrypted contents. Verify sender identity and recorded consent separately. For report delivery, use the recipient's verified certificate. Record delivery separately. No production keys are included.

See the [OpenSSL CMS command reference](https://docs.openssl.org/3.6/man1/openssl-cms/).

## Exercise the private case workflow

Use a future UTC retention date. In these examples replace paths, IDs, and hash with the values returned in your trial. Use the example notes only with a simulated case.

```text
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator open-case --question "Did the fixture contain a programmed temperature step?" --consent-reference fixture-01 --expires YYYY-MM-DD --confirm-authority-and-private-review
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator intake CASE_ID original.csv --device "Synthetic sensor" --captured unknown --clock-context "Simulated clock" --context "Controlled temperature fixture" --expected-sha256 SHA256
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor reviewer verify CASE_ID EVIDENCE_ID --compare original.csv
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator analyze CASE_ID EVIDENCE_ID --interval 60 --threshold 1.5
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor reviewer review CASE_ID --finding Explained --rationale "The fixture contained a programmed step." --tests "Compared CSV observations against fixture inputs." --limitations "Simulated readings only." --reconsider-if "The retained fixture differs from its declared inputs."
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor reviewer report CASE_ID 1 --format html
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator status CASE_ID
```

HTML reports are written to standard output as UTF-8. Redirect only to a new file on the protected volume using a shell that preserves the output bytes. Open the file privately and print to PDF if needed. Use `--correction` with a reason to issue another version. Prior versions remain available until expiry or withdrawal.

## What the pilot records

- The store issues year-based case and evidence IDs. Keep a single pilot store and coordinate numbering with VEIL's case register before using IDs externally. Case, original bytes and checksum, reviews, and recorded custody events are stored transactionally.
- Intake accepts UTF-8 CSV up to 1,000,000 bytes and JPEG, PNG, WAV, MP4 or MOV up to 16 MiB, with a ten-file limit per case. Media checks are basic header checks. Stored media are opaque bytes. Use an approved isolated workflow and scanning before manually viewing third-party media.
- SIGNAL reuses VEIL's deterministic Temperature CSV Audit Bench. It records the input digest, device, declared clock context, code digest, engine version, parameters and flagged source lines with timestamps. The measurements are provisional. The pilot includes no language model, cross-sensor clock calibration, or media interpretation.
- The reviewer checks the original, distinguishes observations from interpretations, records competing explanations, tests, limitations, and evidence that could change the finding. Reviewer names are locally entered identifiers. The application cannot authenticate reviewer identity or guarantee independence. Its custody history records operations through this tool and is editable by anyone who has write access to the database.
- The expiry date is the first UTC day access is blocked. Run `purge-expired --confirm` to remove expired records from the active store. Run `withdraw CASE_ID --confirm` for approved early withdrawal. Before retention closes, document and remove separately held reports, working copies, consent files and backups under the approved policy. Deletion from SQLite does not erase previous filesystem copies or guarantee device-level erasure.
- For backup, close all pilot sessions, copy the SQLite file to encrypted access-controlled media, and test restoration to a separate private directory using only synthetic data at first. Verify a restored original and report. Maintain an external record of withdrawals and expiries so an older backup cannot put a deleted case back into active use.

## Before external intake or fees

Test the intended Windows or Linux host with an invited, consented no-fee case. Verify workstation ACLs and encryption, external identity and consent, backup restoration, media isolation, reviewer independence, encrypted handoff and private delivery on the exact planned setup. An internet intake service would additionally require authenticated uploads, case-scoped permissions, quotas, isolated scanning, audit and incident response, with a deployment outside the public website. No production portal, checkout, account creation, or payment integration is enabled.

[OWASP file upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
