import csv
from config import PENDING_TX_FILE, MINTED_TX_FILE

def save_request(username, email, public_key):
    with open(PENDING_TX_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([username, email, public_key])

def approve_request(username, public_key):
    pending = []
    approved = None
    with open(PENDING_TX_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == username and row[2] == public_key:
                approved = row
            else:
                pending.append(row)

    with open(PENDING_TX_FILE, "w") as f:
        writer = csv.writer(f)
        writer.writerows(pending)

    if approved:
        with open(MINTED_TX_FILE, "a") as f:
            writer = csv.writer(f)
            writer.writerow(approved)

    return approved
