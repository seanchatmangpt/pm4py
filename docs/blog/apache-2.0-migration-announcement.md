---
title: "pm4py is Now Apache 2.0: Open for Enterprise"
date: 2026-04-07
author: "Process Intelligence Solutions"
category: "Announcement"
tags: ["license", "apache", "enterprise", "open-source"]
---

# pm4py is Now Apache 2.0: Open for Enterprise Adoption

We're excited to announce that **pm4py has migrated from AGPL-3.0 to the Apache License 2.0**, effective immediately. This change removes barriers to enterprise adoption while maintaining our commitment to open source.

## Why Apache 2.0?

The AGPL-3.0 license served us well, but it created friction for enterprise users:

| Concern | AGPL-3.0 | Apache 2.0 |
|---------|----------|------------|
| SaaS deployment without source disclosure | ❌ Blocked | ✅ Allowed |
| Embedding in proprietary products | ❌ Viral copyleft | ✅ Permitted |
| Enterprise platform compatibility | ⚠️ Limited | ✅ Full |
| Patent protection | ⚠️ Implicit | ✅ Explicit grant |

**Enterprise feedback was clear:** "We love pm4py, but legal won't approve AGPL."

Apache 2.0 addresses these concerns while keeping pm4py open and free for everyone.

## What This Means For You

### For Users (No Action Required)

If you're using pm4py today, **nothing changes**—except you have *more* freedom:

- ✅ Use in commercial projects
- ✅ Deploy as SaaS without disclosing source
- ✅ Embed in proprietary software
- ✅ Modify without sharing changes
- ✅ All previous AGPL rights preserved

Apache 2.0 is **more permissive** than AGPL-3.0. You don't lose anything.

### For Contributors (One-Time Action Required)

If you've contributed or plan to contribute:

1. **Sign the CLA**: https://cla-assistant.io/process-intelligence-solutions/pm4py
2. **One-time setup**: Takes 2 minutes
3. **Future PRs**: Automatically covered

This ensures we have clear legal authority to distribute your contributions under Apache 2.0.

### For Enterprise Users

**You can now:**

- Integrate pm4py into Snowflake, Databricks, Palantir, or any platform
- Build commercial process mining products on top of pm4py
- Offer pm4py-powered SaaS without opening your code
- Get patent protection from Apache 2.0's explicit grant

**Companies that can now adopt pm4py:**

- Snowflake (for UDFs and native integrations)
- Databricks (for Runtime ML integration)
- Palantir Foundry (for pipeline embedding)
- Proprietary process mining tools
- Internal enterprise tools without legal review blockers

## Dependency Compatibility

All pm4py dependencies are verified for Apache 2.0 compatibility:

| Dependency | License | Compatible |
|------------|---------|------------|
| numpy | BSD | ✅ |
| pandas | BSD | ✅ |
| networkx | BSD | ✅ |
| scipy | BSD | ✅ |
| matplotlib | PSF | ✅ |
| serde (Rust) | Apache-2.0/MIT | ✅ |
| wasm-bindgen | Apache-2.0/MIT | ✅ |

**Note:** `tqdm` uses MPL-2.0 (file-level copyleft), which is compatible. `cvxopt` is GPL-3.0 but is an **optional** dependency only.

## Migration Timeline

| Date | Milestone |
|------|-----------|
| 2026-04-07 | Apache 2.0 license effective |
| 2026-04-07 | CLA bot activated |
| 2026-04-14 | 2.8.0 release with Apache license |
| Ongoing | All new contributions require CLA |

## Legal Authority

This license change is authorized by:

- **Process Intelligence Solutions GmbH** (primary copyright holder)
- **All past contributors** (via Apache 2.0 grant-back clause)
- **Future contributors** (via CLA)

For legal questions: legal@processintelligence.solutions

## FAQ

### Do I need to change anything if I'm using pm4py?

**No.** Apache 2.0 is more permissive. All your existing uses remain valid.

### Can I use pm4py in my commercial product?

**Yes.** You can embed pm4py without opening your source code.

### Do I need to publish my modifications?

**No.** Apache 2.0 doesn't require sharing modifications.

### What about the AGPL "network use" provision?

**Gone.** Apache 2.0 has no network/SaaS copyleft provision.

### Do I still need to attribute pm4py?

**Yes, but minimally.** Keep the existing license notices in redistributed code.

### What if I contributed under AGPL?

**Your contribution is now under Apache 2.0.** By contributing, you grant us the right to relicense.

## Next Steps

1. **Update your dependencies**: `pip install -U pm4py` (version 2.8.0+)
2. **Review your compliance**: If you were avoiding AGPL, you're now clear
3. **Consider contributing**: Sign the CLA and join the community

## Thank You

To our community: thank you for supporting pm4py. This license change is for you—especially those who couldn't use pm4py in enterprise contexts.

**Let's make process mining accessible everywhere.**

---

*For questions: community@processintelligence.solutions*
*For legal matters: legal@processintelligence.solutions*
*GitHub: https://github.com/process-intelligence-solutions/pm4py*
