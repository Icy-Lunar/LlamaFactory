"""Opt-in real-device checks; no model or dataset download is performed."""

import os

import pytest


@pytest.mark.skipif(os.getenv("RUN_WINDOWS_LIGER_SMOKE") != "1", reason="Opt-in Windows accelerator smoke test")
def test_tiny_liger_lora_optimizer_step():
    import torch
    from liger_kernel.transformers import apply_liger_kernel_to_llama
    from peft import LoraConfig, get_peft_model
    from transformers import LlamaConfig, LlamaForCausalLM

    from llamafactory.extras.accelerator import configure_xpu_environment
    from llamafactory.extras.liger import get_model_liger_status
    from llamafactory.extras.misc import get_current_device

    configure_xpu_environment(os.environ)
    device = get_current_device()
    assert device.type in {"xpu", "cuda"}
    assert get_model_liger_status("llama", "bfloat16").enabled
    apply_liger_kernel_to_llama()
    config = LlamaConfig(
        vocab_size=128,
        hidden_size=128,
        intermediate_size=256,
        num_hidden_layers=1,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=128,
        use_cache=False,
    )
    model = LlamaForCausalLM(config).to(device=device, dtype=torch.bfloat16)
    model = get_peft_model(
        model, LoraConfig(r=4, lora_alpha=8, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM")
    )
    model.train()
    tokens = torch.randint(0, 128, (1, 32), device=device)
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=1e-4)
    before = [parameter.detach().clone() for parameter in trainable]
    loss = model(input_ids=tokens, labels=tokens).loss
    assert torch.isfinite(loss)
    loss.backward()
    assert all(parameter.grad is not None and torch.isfinite(parameter.grad).all() for parameter in trainable)
    optimizer.step()
    assert any(not torch.equal(old, parameter) for old, parameter in zip(before, trainable))
