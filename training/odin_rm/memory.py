"""Memory-bounded forward with a full logical-batch loss.

Non-reentrant checkpointing supports integer inputs (no input gradients).
The caller must not update parameters until the complete loss.backward().
"""
import torch
from torch.utils.checkpoint import checkpoint


def checkpointed_pair_scores(pairs, encode_chunk, forward_scores, *, micro_pairs=0):
    if not pairs:
        raise ValueError("Cannot score an empty pair batch")
    if micro_pairs < 0:
        raise ValueError("micro_pairs must be >= 0")
    width = micro_pairs or len(pairs)
    qs, ls = [], []
    for start in range(0, len(pairs), width):
        ids, mask = encode_chunk(pairs[start:start + width])
        if micro_pairs and torch.is_grad_enabled():
            q, ell = checkpoint(
                forward_scores, ids, mask,
                use_reentrant=False, preserve_rng_state=True,
            )
        else:
            q, ell = forward_scores(ids, mask)
        qs.append(q)
        ls.append(ell)
    return torch.cat(qs), torch.cat(ls)
