import underwatch_cv
import time
import asyncio
import buttplug.client as bp

async def main():
    client = bp.ButtplugClient("Underwatch")
    connector = bp.websocket_connector.ButtplugClientWebsocketConnector("ws://127.0.0.1:12345")
    try:
        await client.connect(connector)
        await client.start_scanning()
        await asyncio.sleep(1)
        await client.stop_scanning()
    except bp.ButtplugClientConnectorError as e:
        print(e.message)

    
    timer = 0
    cv = underwatch_cv.ComputerVision()
    last_eliminated_time = 0
    print("Start loop")
    while (True):
        cv.capture_frame()
        if(time.time() - last_eliminated_time > 10):
            if cv.detect_eliminated():
                last_eliminated_time = time.time();
                print("you were eliminated")
        # don't read screen during killcam period
        if(time.time() - last_eliminated_time > 10 or time.time() - last_eliminated_time < 2):
            elims = cv.detect_eliminations()
            assists = cv.detect_assists()
            saves = cv.detect_saves()

            if (elims > 0):
                print("eliminations: "+str(elims))
            if (assists > 0):
                print("assists: "+str(assists))
            if (saves > 0):
                print("saves: "+str(saves))

            for device in client.devices.values():
                if "VibrateCmd" in device.allowed_messages.keys():
                    await device.send_vibrate_cmd((elims+assists+saves)/3)
        await asyncio.sleep(.2)

asyncio.run(main())