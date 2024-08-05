import socket
import json
import time

HOST = '127.0.0.1'
PORT = 65432


def print_toy_auction_table(toy_data):
    def format_time_left(end_time):
        time_left = end_time - time.time()
        if time_left <= 0:
            return "Auction ended"
        hours, rem = divmod(time_left, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def format_table(data, headers):
        col_widths = [max(len(str(item)) for item in col) for col in zip(*data, headers)]
        header_row = " | ".join(f"{header:<{width}}" for header, width in zip(headers, col_widths))
        separator = "-+-".join("-" * width for width in col_widths)
        data_rows = [" | ".join(f"{str(item):<{width}}" for item, width in zip(row, col_widths)) for row in data]
        return "\n".join([header_row, separator] + data_rows)

    table_data = []
    for toy_id, toy in toy_data.items():
        table_data.append([
            toy_id,
            toy['name'],
            toy['description'],
            f"${toy['starting_price']}",
            f"${toy['current_price']}",
            toy['highest_bidder'] or "No bids",
            format_time_left(toy['auction_end'])
        ])

    headers = ["ID", "Name", "Description", "Starting Price", "Current Price", "Highest Bidder", "Time Left"]
    print(format_table(table_data, headers))


def receive_data(sock):
    data = b''
    while True:
        part = sock.recv(4096)
        data += part
        if len(part) < 4096:
            break
    return data.decode('utf-8')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        username = input("Enter your username to login: ")
        s.sendall(f"LOGIN {username}".encode('utf-8'))
        data = s.recv(1024).decode('utf-8')

        if data == 'SUCCESS':
            print(f"SUCCESS: Logged in as {username}")

            while True:
                print("\nToy Auction Menu:")
                print("1. List auctions")
                print("2. Place bid")
                print("3. Logout")

                choice = input("Enter your choice (1-3): ")
                if choice == '1':
                    s.sendall("VIEW".encode('utf-8'))
                    data = receive_data(s)
                    try:
                        listings = json.loads(data)
                        if listings:
                            print_toy_auction_table(listings)
                        else:
                            print("ERROR: No auctions available.")
                    except json.JSONDecodeError as e:
                        print(f"ERROR: Error decoding JSON: {e}")
                elif choice == '2':
                    toy_id = input("Enter toy ID to bid on: ")
                    bid_amount = input("Enter your bid amount: ")
                    s.sendall(f"BID {toy_id} {bid_amount}".encode('utf-8'))
                    data = s.recv(1024).decode('utf-8')
                    if data.startswith("SUCCESS"):
                        print(f"SUCCESS: Bid placed successfully. New bid amount: {data.split()[1]}")
                    elif data.startswith("ERROR"):
                        print(f"ERROR: Error placing bid: {data}")
                elif choice == '3':
                    print("SUCCESS: Logging out.")
                    break
                else:
                    print("ERROR: Invalid choice. Please try again.")

        else:
            print(f"ERROR: Login failed: {data}")


if __name__ == "__main__":
    main()
