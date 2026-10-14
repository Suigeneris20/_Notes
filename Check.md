I want you to act as a senior software engineer doing pre-production regression validation. Read every file in the `PFIX` folder and build a working understanding of its architecture, process flow, known issues, documented fixes, and edge cases. Your job is to design edge-case simulations that confirm my Checkmarx-related changes broke nothing before this system goes live in PROD.

**Ground everything in the PFIX folder.** Every edge case, simulation, and solution you give me must come from the files in that folder. Where the files don't cover something, say so explicitly rather than filling the gap with assumptions. This matters because I will run these tests against production-bound code and need to trust that each recommendation traces back to something real in the system.

**Edge cases to cover:** The examples I care about most are batch resetting and simulation/pricing retriggering. Identify any other corner or edge cases the PFIX files reveal, including failure modes, known issues, and previously applied fixes that my Checkmarx changes could have regressed. Note where my changes plausibly interact with each case.

**For each edge case, give me:**
1. A short description of the scenario and why my Checkmarx changes could affect it
2. Step-by-step instructions to simulate or run the case
3. The expected correct behavior or solution, paired directly with those instructions
4. The specific file(s) in the PFIX folder where you found the basis for it (file name, and the relevant section, function, or line where possible)

Keep each instruction and its paired solution together so I can execute them one at a time. If a file contains the evidence for several cases, cite it each time. If a case needs setup (test data, config flags, environment state), include that in the instructions.
