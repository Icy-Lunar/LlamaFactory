# System driver staging directory

Windows system drivers are hardware-specific and are not redistributed with this project. Put one vendor-approved
installer in this directory before using `--driver-mode install`:

- NVIDIA CUDA: a signed NVIDIA display-driver installer whose filename contains `nvidia` or `cuda`.
- AMD ROCm: the ROCm-compatible AMD Software installer whose filename contains `amd` or `radeon`.

The unified launcher can also receive an exact local path with `--driver-installer` or an official HTTPS download URL
with `--driver-url`. Driver installation requires an elevated PowerShell window and always stops before Python package
installation so the host can be rebooted first.
