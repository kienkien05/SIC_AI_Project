from __future__ import annotations

import math

import torch
from torch import Tensor, nn
from torch.nn import functional as F
from torchvision import models


class FaceEmbeddingNet(nn.Module):
    def __init__(
        self,
        backbone: str = "resnet18",
        embedding_dim: int = 512,
        pretrained: bool = True,
    ) -> None:
        super().__init__()
        if backbone == "resnet18":
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            network = models.resnet18(weights=weights)
        elif backbone == "resnet50":
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            network = models.resnet50(weights=weights)
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        feature_dim = network.fc.in_features
        network.fc = nn.Identity()
        self.backbone_name = backbone
        self.backbone = network
        self.embedding = nn.Linear(feature_dim, embedding_dim, bias=False)
        self.embedding_bn = nn.BatchNorm1d(embedding_dim)

    def forward(self, images: Tensor) -> Tensor:
        features = self.backbone(images)
        embeddings = self.embedding_bn(self.embedding(features))
        return F.normalize(embeddings, p=2, dim=1)


class ArcMarginProduct(nn.Module):
    def __init__(
        self,
        embedding_dim: int,
        class_count: int,
        margin: float = 0.5,
        scale: float = 64.0,
        easy_margin: bool = False,
    ) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(class_count, embedding_dim))
        nn.init.xavier_uniform_(self.weight)
        self.margin = margin
        self.scale = scale
        self.easy_margin = easy_margin
        self.cos_m = math.cos(margin)
        self.sin_m = math.sin(margin)
        self.threshold = math.cos(math.pi - margin)
        self.mm = math.sin(math.pi - margin) * margin

    def forward(self, embeddings: Tensor, labels: Tensor) -> Tensor:
        cosine = F.linear(F.normalize(embeddings), F.normalize(self.weight))
        sine = torch.sqrt(torch.clamp(1.0 - cosine.square(), min=1e-7))
        phi = cosine * self.cos_m - sine * self.sin_m
        if self.easy_margin:
            phi = torch.where(cosine > 0, phi, cosine)
        else:
            phi = torch.where(cosine > self.threshold, phi, cosine - self.mm)
        one_hot = torch.zeros_like(cosine)
        one_hot.scatter_(1, labels.view(-1, 1).long(), 1.0)
        return (one_hot * phi + (1.0 - one_hot) * cosine) * self.scale
