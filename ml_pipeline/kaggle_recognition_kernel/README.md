# Model 2 - Face Recognition

Simple teaching pipeline for Model 2:

1. Use aligned identities from WebFace.
2. Run EDA: count identities/images and display face samples.
3. Resize, augment, standardize, and split per identity.
4. Fine-tune FaceNet VGGFace2 with a compact ArcFace head.
5. Save `facenet_best.pt`, build a 512-D gallery, and test cosine similarity.

At deployment: Model 1 YOLO crops faces; Model 2 returns embeddings; cosine search matches five enrolled student embeddings. The ArcFace head is training-only.
