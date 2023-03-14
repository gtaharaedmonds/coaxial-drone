import asyncio
from mavsdk import System

# TODO: improve mavsdk_server build process

async def test():
    drone = System()
    await drone.connect('serial://COM5:57600')

    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break
    # old_gcs_sysid = await drone.param.get_param_int('SYSID_MYGCS')
    while True:
        await drone.manual_control.set_manual_control_input(
            x=0.85, y=0.0, z=0, r=0.0
        )
        await asyncio.sleep(0.05)

if __name__ == '__main__':
    asyncio.run(test())