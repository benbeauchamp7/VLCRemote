import asyncio
import subprocess
import json
import websockets
from VLC import VLC
import os


vlc = VLC()
commands = {
    "play": vlc.play,
    "pause": vlc.pause,
    "resume": vlc.resume,
    "seek": vlc.seek,
    "seek_by": vlc.seek_by,
    "set_tracks": vlc.set_tracks
}

async def send(websocket):
    while True:
        await websocket.send(json.dumps({
            "type": "vlc",
            "title": vlc.get_title(),
            "length": vlc.get_length() / 1000,
            "time": vlc.get_time() / 1000,
            "playing": vlc.get_playing()
        }))
        await asyncio.sleep(1)

async def recv(websocket):
    async for message in websocket:
        if message.find(':') == -1:
            message += ':'
        [command], args = [arg.split(';#;') for arg in message.split(':')]

        if (command in commands.keys()):
            commands[command](*args)

            await asyncio.sleep(0.01)
            await websocket.send(json.dumps({
                "type": "vlc",
                "title": vlc.get_title(),
                "length": vlc.get_length() / 1000,
                "time": vlc.get_time() / 1000,
                "playing": vlc.get_playing()
            }))
        elif (command == "files_in"):
            query = args[0]
            if not query:
                query = '/media/shared/Shows/'

            if os.path.isdir(query):
                valid = lambda q, d: d[0] != '.' and (os.path.isdir(q + d) or d[-3:] in ['mkv', 'mp4', 'm4v'])
                await websocket.send(json.dumps({
                    "type": "fs",
                    "f_dir": query,
                    "f_resp": {d: os.path.isdir(query + d) for d in sorted(os.listdir(query)) if valid(query, d)}
                }))
            else:
                await websocket.send(json.dumps({
                    "type": "fs",
                    "f_dir": query,
                    "f_resp": {}
                }))
        elif (command == "tracks"):
            data = vlc.get_tracks()
            subs = [[int(e[0]), e[1].decode('utf-8')] for e in data['subs']]
            audio = [[int(e[0]), e[1].decode('utf-8')] for e in data['audio']]

            await websocket.send(json.dumps({
                "type": "tracks",
                "subs": json.dumps(subs),
                "audio": json.dumps(audio)
            }))
        

async def run(websocket):
    await asyncio.gather(
        send(websocket),
        recv(websocket)
    )

async def main():
    async with websockets.serve(run, "0.0.0.0", 8901):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    # sub = subprocess.Popen(['python3', 'httpserver.py']);
    asyncio.run(main())
