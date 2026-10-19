# A dream candidate needs a reproducible failure

A weekly replay can turn a single agent's confident summary into a lasting memory
rule. If the summary was wrong, the next run inherits the mistake. The useful
boundary is the candidate plus its source trace, the exact proposed change, and a
check capable of rejecting it. Keep those together through review.

Start with the committed portfolio sample and run the documented `run` command
into a scratch output directory. Preserve the source log and generated index.
For each candidate, a reviewer should answer three concrete questions: which
observed failure justifies this change, which existing behavior could it break,
and what result would cause us to reject it? A missing source is a reason to
request evidence, not an invitation to write a more persuasive rationale.

For a candidate memory such as "retry a failed write," include a counterexample:
the first attempt might have succeeded while its acknowledgement was lost. A safe
candidate might instead say to inspect the target or use an idempotency key before
repeating an effect. Test it against both a genuine failed write and an uncertain
outcome. The replay runner proposes text; it cannot infer the service's retry
contract from a completion sentence.

Keep the replay input fixed while comparing the old and candidate behavior.
Record wall time, extra reads, retries and accepted results alongside token use.
A shorter memory can force the agent to reconstruct facts it previously retained,
so token count alone is an incomplete adoption criterion. This is an experiment
to run on the portfolio, not a measured efficiency claim about this CLI.

The current human promotion boundary remains in force. A reviewer may submit a
candidate to `review-queue`; no file in this example authorizes memory writes,
automatic skill installation or external posting. After a prompt, source or tool
change, preserve the old candidate and assess whether its checks still apply.

This procedure applies the reviewer question raised by
[Audit Without Verification](https://arxiv.org/abs/2609.07680).
It adds a review protocol around this deterministic CLI; it does not implement a
controller that enforces the protocol automatically.
