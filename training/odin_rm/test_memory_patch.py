"""Standalone tests: python training/odin_rm/test_memory_patch.py (CPU, no weights)."""
import copy
import importlib.util
from pathlib import Path
import unittest
import torch
from torch import nn

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

m = load('modeling')
mem = load('memory')

class Tiny(nn.Module):
    def __init__(self, dropout=0.):
        super().__init__()
        self.embed = nn.Embedding(32, 8)
        self.embed.weight.requires_grad_(False)
        self.suffix = nn.Sequential(nn.Linear(8, 8), nn.Tanh(), nn.Dropout(dropout))
        self.head_q = m._weight_norm_linear(8)
        self.head_l = m._weight_norm_linear(8)
    def forward(self, ids, mask):
        h = m.last_token_hidden(self.suffix(self.embed(ids)), mask)
        return (m.positive_score(self.head_q(h).squeeze(-1)),
                m.positive_score(self.head_l(h).squeeze(-1)))

ROWS = [[1,2,3], [2,4], [5,6,7,8], [9], [10,11], [12,13,14], [15], [16,17,18,19]]
def encode(pairs):
    rows = [ROWS[2*i+j] for i in pairs for j in (0,1)]
    ids = torch.zeros(len(rows), max(map(len, rows)), dtype=torch.long)
    mask = torch.zeros_like(ids)
    for i, row in enumerate(rows):
        ids[i,:len(row)] = torch.tensor(row)
        mask[i,:len(row)] = 1
    return ids, mask

def loss_for(net, q, ell):
    return m.odin_rm_loss(q[::2], ell[::2], q[1::2], ell[1::2],
        torch.tensor([3,4,2,1]), torch.tensor([2,1,3,4]),
        torch.tensor([.9,.8,.7,.9]), torch.tensor([.4,.3,.2,.5]),
        head_q=net.head_q, head_l=net.head_l)[0]

def run(net, micro, direct_chunks=False):
    torch.manual_seed(91)
    if direct_chunks:
        scores = [net(*encode([i])) for i in range(4)]
        q, ell = (torch.cat([s[j] for s in scores]) for j in (0,1))
    else:
        q, ell = mem.checkpointed_pair_scores(list(range(4)), encode, net, micro_pairs=micro)
    loss = loss_for(net,q,ell)
    loss.backward()
    return q.detach(), loss.detach(), {n:p.grad.clone() for n,p in net.named_parameters() if p.requires_grad}

class MemoryTests(unittest.TestCase):
    def test_full_loss_and_all_parameter_gradients(self):
        torch.manual_seed(3)
        base = Tiny()
        a = run(copy.deepcopy(base), 0)
        for width in (1,2,3,4):
            b = run(copy.deepcopy(base), width)
            torch.testing.assert_close(a[0],b[0],rtol=2e-5,atol=2e-6)
            torch.testing.assert_close(a[1],b[1],rtol=2e-5,atol=2e-6)
            for name in a[2]:
                torch.testing.assert_close(a[2][name],b[2][name],rtol=3e-5,atol=3e-6)
    def test_dropout_replay(self):
        torch.manual_seed(4)
        base = Tiny(dropout=.25)
        a = run(copy.deepcopy(base),1,direct_chunks=True)
        b = run(copy.deepcopy(base),1)
        for name in a[2]:
            torch.testing.assert_close(a[2][name],b[2][name])
    def test_no_grad_eval(self):
        net=Tiny()
        with torch.no_grad():
            q,ell=mem.checkpointed_pair_scores(list(range(4)),encode,net,micro_pairs=1)
        self.assertEqual(q.shape,(8,))
        self.assertFalse(q.requires_grad)
    def test_uniform_length_loss(self):
        q=torch.ones(4)
        length=torch.arange(4.)
        loss,_,_=m.length_correlation_loss(q,q,length)
        torch.testing.assert_close(2*loss, torch.tensor(4*__import__('math').log(2)))

class QwenTests(unittest.TestCase):
    def test_qwen_frozen_prefix_and_suffix_gradients(self):
        from transformers import Qwen2Config, Qwen2ForCausalLM
        torch.manual_seed(9)
        config = Qwen2Config(vocab_size=32, hidden_size=16, intermediate_size=32,
                            num_hidden_layers=3, num_attention_heads=2,
                            num_key_value_heads=2, attention_dropout=0.0)
        config._attn_implementation = "eager"
        base = m.DualHeadRewardModel(Qwen2ForCausalLM(config))
        m.unfreeze_last_layers(base.backbone, 2)
        states = []
        for width in (0, 1):
            # weight-normalized modules contain cached tensors after forward;
            # copy before any forward, then load the same state.
            rm = m.DualHeadRewardModel(Qwen2ForCausalLM(config))
            rm.load_state_dict(base.state_dict())
            m.unfreeze_last_layers(rm.backbone, 2)
            def scores(ids, mask):
                return rm.scores_from_hidden(m.last_token_from_inner(rm, ids, mask, 2))
            q, ell = mem.checkpointed_pair_scores(list(range(4)), encode, scores, micro_pairs=width)
            loss = loss_for(rm, q, ell)
            loss.backward()
            self.assertIsNone(rm.backbone.model.layers[0].self_attn.q_proj.weight.grad)
            grads = {n:p.grad.detach().clone() for n,p in rm.named_parameters() if p.requires_grad}
            states.append((q.detach(), loss.detach(), grads))
        a,b=states
        torch.testing.assert_close(a[0],b[0],rtol=1e-4,atol=1e-5)
        torch.testing.assert_close(a[1],b[1],rtol=1e-4,atol=1e-5)
        for name in a[2]:
            torch.testing.assert_close(a[2][name],b[2][name],rtol=2e-4,atol=2e-5)

class LoopTests(unittest.TestCase):
    def test_real_training_loop_two_updates_with_holdout(self):
        # Load actual local functions without unavailable business-config imports.
        import ast, logging, math, random, typing
        source = ast.parse((HERE / "train_rm.py").read_text(encoding="utf-8"))
        body = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
        body += [n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        ns = dict(vars(typing))
        ns.update(vars(m))
        ns.update(torch=torch, math=math, random=random, Path=Path,
                  logger=logging.getLogger("test"),
                  checkpointed_pair_scores=mem.checkpointed_pair_scores)
        exec(compile(ast.fix_missing_locations(ast.Module(body=body,type_ignores=[])),str(HERE / "train_rm.py"),"exec"),ns)
        from transformers import Qwen2Config,Qwen2ForCausalLM
        cfg=Qwen2Config(vocab_size=32,hidden_size=16,intermediate_size=32,
                       num_hidden_layers=3,num_attention_heads=2,num_key_value_heads=2)
        cfg._attn_implementation="eager"
        rm=m.DualHeadRewardModel(Qwen2ForCausalLM(cfg))
        m.unfreeze_last_layers(rm.backbone,2)
        pairs=[]; cache={}
        for i in range(4):
            sides=[]
            for j in range(2):
                side=dict(group_id=str(i),candidate_index=j,n_tokens=len(ROWS[2*i+j]),
                          teacher_score=.9 if j==0 else .4)
                cache[ns['_side_key'](side)]=ROWS[2*i+j]
                sides.append(side)
            pairs.append(dict(chosen=sides[0],rejected=sides[1]))
        history,best=ns['train_unfrozen_suffix'](
            rm,cache,pairs,pairs,device=torch.device('cpu'),pad_id=0,n_unfreeze=2,
            tuned_names=[n for n,p in rm.backbone.named_parameters() if p.requires_grad],
            epochs=2,batch=4,lr=1e-4,layer_lr=1e-5,
            lambda_l=.1,lambda_o=1.,lambda_gap=10.,log_every=1,
            patience_evals=0,min_epochs=1,seed=0,micro_pairs=1)
        self.assertEqual(len(history),2)
        self.assertTrue(all(torch.isfinite(p).all() for p in rm.parameters()))
        self.assertTrue(all(p.grad is None for p in rm.parameters()))
        self.assertIn('q_std',history[-1]['holdout'])

if __name__ == '__main__':
    unittest.main()
