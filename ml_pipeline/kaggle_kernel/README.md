# Kaggle kernel package

This private Kaggle Kernel runs the baseline recognition trainer against `nanimasaka/masked-face-recognition-dataset` with a T4 GPU request.

Push after rotating the exposed Kaggle credential:

```powershell
kaggle kernels push -p C:\Users\dangv\Desktop\SIC\ml_pipeline\kaggle_kernel --accelerator GPU
```

Kaggle saves training artifacts under `/kaggle/working/face-attendance-baseline/recognition`.

To train a different dataset, update `DATA_ROOT`, `source`, `scenario`, and `subject_mode` in `train_kernel.py`, then push a new version.
