import socket
import threading
import time
import json

HOST = '127.0.0.1' 
PORT = 65432  

listings = {
    "Toy1": {"name": "Robot Plush", "description": "Cute robot plush toy", "starting_price": 10,
             "current_price": 10, "highest_bidder": None, "auction_end": time.time() + 20},  #  20 secs
    "Toy2": {"name": "Rainbow Unicorn", "description": "Rainbow-colored unicorn figurine",
             "starting_price": 25, "current_price": 25, "highest_bidder": None, "auction_end": time.time() + 600},  # 10 mins
    "Toy3": {"name": "Space Explorer", "description": "Action figure of a space explorer",
             "starting_price": 15, "current_price": 15, "highest_bidder": None, "auction_end": time.time() + 900},  # 15 mins
    "Toy4": {"name": "Miniature Dragon", "description": "Detailed miniature dragon model",
             "starting_price": 30, "current_price": 30, "highest_bidder": None, "auction_end": time.time() + 1200},  # 20 mins
    "Toy5": {"name": "Pirate Ship", "description": "Wooden pirate ship model",
             "starting_price": 40, "current_price": 40, "highest_bidder": None, "auction_end": time.time() + 1500}  # 25 mins
}

users = {
    "user1",
    "user2"
}

def handle_client(conn, addr):
    print(f'Connected by {addr}')
    username = None

    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
        except:
            break

        if not data:
            break
        print(f'Received: {data}')

        command = data.split()[0]

        if command == 'LOGIN':
            username = data.split()[1]
            if username in users:
                conn.sendall('SUCCESS'.encode('utf-8'))
                username = username
            else:
                conn.sendall('ERROR Username not found'.encode('utf-8'))
        elif command == 'VIEW':
            response = json.dumps(listings)
            conn.sendall(response.encode('utf-8'))
        elif command == 'BID':
            toy_id, bid_amount = data.split()[1:]
            if toy_id in listings and listings[toy_id]["auction_end"] > time.time():
                if int(bid_amount) > listings[toy_id]["current_price"]:
                    listings[toy_id]["current_price"] = int(bid_amount)
                    listings[toy_id]["highest_bidder"] = username
                    conn.sendall(f'SUCCESS {bid_amount}'.encode('utf-8'))
                else:
                    conn.sendall('ERROR Bid too low'.encode('utf-8'))
            else:
                conn.sendall('ERROR Invalid toy ID or auction closed'.encode('utf-8'))
        else:
            conn.sendall('ERROR Unknown command'.encode('utf-8'))

    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Server started on port', PORT)
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
