from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DeviceBundleItem:
    name: str
    note: str


@dataclass(slots=True, frozen=True)
class ArmDeviceSpec:
    name: str
    soc: str
    cpu: str
    gpu: str
    npu: str
    ram: str
    storage: str
    connectivity: str
    camera_interface: str
    power: str
    supported_os: tuple[str, ...]
    bundle: tuple[DeviceBundleItem, ...]


@dataclass(slots=True, frozen=True)
class RuntimeSnapshot:
    cpu_temperature_c: float
    memory_pressure_percent: float
    capture_fps: float
    power_draw_watts: float


class OrangePi5PlusEmulator:
    def __init__(self, spec: ArmDeviceSpec | None = None) -> None:
        self.spec = spec or orange_pi_5_plus_spec()

    def runtime_snapshot(self, frame_index: int) -> RuntimeSnapshot:
        base_temp = 57.0 + min(frame_index, 10) * 1.8
        base_memory = 33.0 + min(frame_index, 10) * 3.2
        capture_fps = max(9.0, 29.0 - frame_index * 1.5)
        power_draw = 8.1 + min(frame_index, 10) * 0.45
        return RuntimeSnapshot(
            cpu_temperature_c=round(base_temp, 2),
            memory_pressure_percent=round(base_memory, 2),
            capture_fps=round(capture_fps, 2),
            power_draw_watts=round(power_draw, 2),
        )


def orange_pi_5_plus_spec() -> ArmDeviceSpec:
    return ArmDeviceSpec(
        name="Orange Pi 5 Plus",
        soc="Rockchip RK3588",
        cpu="8-core 64-bit: 4x Cortex-A76 @ 2.4GHz + 4x Cortex-A55 @ 1.8GHz",
        gpu="Arm Mali-G610",
        npu="Embedded NPU up to 6 TOPS",
        ram="16GB LPDDR4/4x",
        storage="microSD, eMMC socket, M.2 2280 NVMe, optional 512GB SSD bundle",
        connectivity="Dual 2.5GbE, Wi-Fi 6 / Bluetooth module support",
        camera_interface="1x MIPI CSI 4-lane",
        power="USB-C 5V@4A",
        supported_os=("OrangePi OS (Droid)", "OrangePi OS (Arch)", "Ubuntu 22.04", "Debian 11", "Android 12"),
        bundle=(
            DeviceBundleItem(name="Board", note="Orange Pi 5 Plus main board"),
            DeviceBundleItem(name="Power Supply", note="USB-C power adapter"),
            DeviceBundleItem(name="Heat dissipation shell", note="Active cooling enclosure"),
            DeviceBundleItem(name="WiFi6 module", note="M.2 2230 connectivity module"),
            DeviceBundleItem(name="512G Hard Drive", note="Bundled NVMe storage"),
        ),
    )
