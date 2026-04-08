# CLA (Contributor License Agreement) Setup Guide

This document describes the CLA infrastructure for pm4py Apache 2.0 migration.

## Why a CLA?

With the Apache 2.0 license migration, we need a CLA to:

1. **Verify contributor identity** (prevent impersonation)
2. **Get explicit Apache 2.0 grant** (clear legal authority)
3. **Grant patent rights** (Apache 2.0 includes patent clause)
4. **Protect the project** (defend against infringement claims)

## Recommended Solution: CLA Assistant

**CLA Assistant** (https://cla-assistant.io/) is the recommended solution:

- ✅ Free for open source
- ✅ GitHub-native (no external accounts)
- ✅ Automatic PR blocking
- ✅ Simple web-based signing
- ✅ Supports individual and corporate CLAs

## Setup Instructions

### 1. Create CLA Documents

Create two CLA documents in `.github/cla/`:

#### Individual CLA (`.github/cla/individual-cla.md`)

```markdown
# Individual Contributor License Agreement

Thank you for your interest in contributing to pm4py ("We" or "Us").

This Individual Contributor License Agreement ("Agreement") sets out the terms governing your use of the software and your contributions to the project.

## 1. Definitions

"You" (or "Your") shall mean the copyright owner or legal entity authorized by the copyright owner that is making this Agreement with Us. "Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity.

## 2. Grant of Copyright License

Subject to the terms and conditions of this Agreement, You hereby grant to Us a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute Your contributions and such derivative works.

## 3. Grant of Patent License

Subject to the terms and conditions of this Agreement, You hereby grant to Us a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work, where such license applies only to those patent claims licensable by You that are necessarily infringed by Your contribution(s) alone or by combination of Your contribution(s) with the Work to which such contribution(s) was submitted.

## 4. Notice

You agree to include a notice of copyright and license in each contribution You submit.

## 5. Representations

You represent that You are legally entitled to grant the above license. You represent that each of Your contributions is Your original creation. You represent that You have the right to submit the contributions.

## 6. Disclaimer

THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED INCLUDING, WITHOUT LIMITATION, ANY WARRANTIES OR CONDITIONS OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.

## 7. Agreement

You accept and agree to the terms of this Agreement by clicking "I Agree" below.

**Copyright Owner:** __________________________

**Name:** __________________________

**Title:** __________________________

**GitHub Username:** __________________________

**Email:** __________________________

**Date:** __________________________
```

#### Corporate CLA (`.github/cla/corporate-cla.md`)

```markdown
# Corporate Contributor License Agreement

This Corporate Contributor License Agreement ("Corporate CLA") is entered into between __________________________ ("Company") and Process Intelligence Solutions GmbH ("Project").

## 1. Grant of Copyright License

Company hereby grants to Project a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute the Company's contributions.

## 2. Grant of Patent License

Company hereby grants to Project a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work.

## 3. Authorized Contributors

Company designates the following individuals as authorized to contribute on behalf of Company:

1. __________________________ (GitHub: __________________)
2. __________________________ (GitHub: __________________)
3. __________________________ (GitHub: __________________)

## 4. Representative Warranty

Company represents that Company is legally entitled to grant the above license.

**Company Name:** __________________________

**Signature:** __________________________

**Name:** __________________________

**Title:** __________________________

**Date:** __________________________
```

### 2. Enable CLA Assistant

1. Visit: https://cla-assistant.io/
2. Click "Install" for your GitHub account
3. Select the pm4py repository
4. Configure:
   - CLA documents location: `.github/cla/`
   - PR blocking: Enabled
   - Signed CLAs storage: `.github/cla-signed/`

### 3. Configure GitHub Branch Protection

1. Go to repository Settings → Branches
2. Add rule for `release` branch:
   - ✅ Require status checks to pass before merging
   - ✅ Require "CLA Assistant" check
   - ✅ Require pull request reviews

### 4. Verify Setup

Test the CLA flow:

1. Create a test PR from a new fork
2. Verify PR is blocked with "CLA not signed" message
3. Sign CLA via provided link
4. Verify PR check passes

## Alternative: Simple CLA Bot

If CLA Assistant is unavailable, alternatives include:

- **EasyCLA**: https://easycla.io/
- **CLA Bot**: https://github.com/cla-assistant/cla-assistant
- **Custom GitHub Action**: See `.github/workflows/cla-check.yml`

## CLA Status Tracking

Track CLA signatures in `.github/cla-signed/`:

```
.github/cla-signed/
├── individual/
│   ├── username1.json
│   └── username2.json
└── corporate/
    └── company1.json
```

## Emergency CLA (Paper Backup)

For contributors who cannot use the web CLA:

1. Print the Individual CLA
2. Sign and date
3. Scan and email to: legal@processintelligence.solutions
4. Maintainers manually add to `.github/cla-signed/`

## Questions?

For CLA-related questions: legal@processintelligence.solutions

For technical issues: https://github.com/process-intelligence-solutions/pm4py/issues
