# Submission guide

The package fulfills the local computational/document deliverables of Phase 1. The assignment also requires course registration and a GitHub repository workflow. Neither a remote upload nor a registration is claimed here.

1. Read the Persian report, `PROJECT_CARD.md` and `AI_USAGE.md`. Independently check the code and be prepared to explain why the target is a weak label, why price is excluded, why the split uses parent products and what URL-only image availability means.
2. Check current official course/CW announcements. The supplied PDF says official website/starter-file links will be announced; none were supplied here. No unofficial starter code is represented as course-provided code.
3. Register the selected question/subset in the course's central list if not already registered. Similarity checks and any later topic approval are course processes, not something this package can certify.
4. Recover the included local Git history with `git clone phase1-history.bundle phase1-repository`. Inspect `git show phase-1` and `git tag --list`. Do not invent an earlier commit date; the delivered tag records actual package preparation.
5. Create/use your real GitHub repository. Add it as the remote and push the recovered branch and `phase-1` tag. Use your actual URL; this guide intentionally contains no fabricated repository link. Do not commit `data/raw`, processed row-level exports or reviewer text.
6. If a phase-one CW upload is open, follow its exact file-naming and upload rules. This ZIP includes the assignment-required `reports/phase1.pdf`; it also includes a presentation and LaTeX sources at the user's request.

For later phases, keep this tag immutable and work on new commits. Perform modeling only after freezing input availability and transformations. The final-project student-recorded video/oral defense are not replaced by these slides or speaker notes.

The archive checksum manifest can verify extracted bytes. The Git bundle tracks sources, aggregate outputs, reports, documentation and the local phase-one tag; raw data remains outside Git but is included in the private ZIP for offline reproduction. If cloning the bundle, copy the ZIP's `data/raw/` into the clone before an offline run.
