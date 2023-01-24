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

    score = 0
    decay_per_second = 10
    points_per_popup = 40
    popup_duration = 2.8
    last_eliminated_time = 0
    cv = underwatch_cv.ComputerVision()
    while (True):
        loop_starting_time = time.time()
        elims = 0
        assists = 0
        saves = 0
        cv.capture_popup_frame()

        if(time.time() - last_eliminated_time > 10):
            if cv.detect_eliminated():
                last_eliminated_time = time.time()
                print("you were eliminated")

        # don't read screen during killcam period
        if(time.time() - last_eliminated_time > 10 or time.time() - last_eliminated_time < 2):
            elims = cv.detect_eliminations()
            assists = cv.detect_assists()
            saves = cv.detect_saves()
            # print(str(1000*(time.time()-loop_starting_time)) + "ms")
            
        await_time_before_next_update = .2 - (time.time()-loop_starting_time)
        await asyncio.sleep(await_time_before_next_update)

        delta_time = time.time() - loop_starting_time
        total = elims+assists+saves
        score += delta_time * total * points_per_popup / popup_duration
        if(total == 0):
            score -= delta_time * decay_per_second
        if(score < 0):
            score = 0
        print("score: " + str(int(score)))

        for device in client.devices.values():
            if "VibrateCmd" in device.allowed_messages.keys():
                await device.send_vibrate_cmd(score/100)

asyncio.run(main())