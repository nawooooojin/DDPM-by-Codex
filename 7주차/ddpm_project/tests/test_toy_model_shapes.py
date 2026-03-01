import torch

from src.models import LitClassifier, ToyMLP



def test_toy_mlp_output_shape() -> None:
    net = ToyMLP(input_dim=20, hidden_dim=16, num_classes=4, dropout=0.0)
    x = torch.randn(8, 20)
    logits = net(x)
    assert logits.shape == (8, 4)



def test_lit_classifier_output_shape() -> None:
    model = LitClassifier(
        net=ToyMLP(input_dim=20, hidden_dim=16, num_classes=4, dropout=0.0),
        lr=1e-3,
        weight_decay=0.0,
        num_classes=4,
    )
    x = torch.randn(5, 20)
    logits = model(x)
    assert logits.shape == (5, 4)
