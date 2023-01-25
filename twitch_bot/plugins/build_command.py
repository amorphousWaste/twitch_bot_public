"""Test plugin."""

from plugins._base_plugins import BaseCommandPlugin


class BuildCommand(BaseCommandPlugin):
    """Build plugin."""

    COMMAND = 'build'

    async def run(self) -> None:
        """Computer build info."""
        await self.send_message(
            'Motherboard: MSI B150I Gaming Pro AC; '
            'RAM: G.SKILL Aegis 32GB (2x16GB) DDR4; '
            'CPU: Intel Core i7-6700 Quad-core 3.4GHz; '
            'PSU: Corsair SF750 750W 80+ Platinum Modular SFX; '
            'GPU: ASUS ROG STRIX 3080 RTX; '
        )
        await self.send_message(
            'Case: Phanteks Evolv Shift 2 Air Mini-ITX Case; '
            'OS: Windows 10 Home OEM'
            'Boot: Western Digital WD_BLACK SN750 1TB M.2 2280 SSD; '
            'Data01: Western Digital Green 3TB HDD; '
            'Data02: Western Digital Black 6TB HDD'
        )
        await self.send_message('https://ca.pcpartpicker.com/list/fLwmwz')
