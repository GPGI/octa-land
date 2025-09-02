import os
from utils.deploy import deploy_contract
from utils.mint import mint_land
from utils.helpers import save_request, approve_request
from config import TOKEN_ADDRESS

def main():
    global TOKEN_ADDRESS

    # Deploy on startup
    if not TOKEN_ADDRESS:
        print("Deploying contract...")
        TOKEN_ADDRESS = deploy_contract()

    while True:
        print("\n--- Octa City Shell ---")
        print("1. Request Land")
        print("2. Approve Land (Admin)")
        print("3. Exit")
        choice = input("Select: ")

        if choice == "1":
            username = input("Enter username: ")
            email = input("Enter email: ")
            public_key = input("Enter public wallet address: ")
            save_request(username, email, public_key)
            print("✅ Land request saved. Waiting for admin approval.")

        elif choice == "2":
            username = input("Enter username to approve: ")
            public_key = input("Enter wallet address to approve: ")
            approved = approve_request(username, public_key)
            if approved:
                mint_land(public_key)
                print("✅ Land minted and recorded.")
            else:
                print("❌ No matching request found.")

        elif choice == "3":
            break

if __name__ == "__main__":
    main()
