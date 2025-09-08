# python_shell/main.py
import sys
from .admin_panel import AdminPanel
from .city_panel import CityPanel
from .sarakt_panel import SaraktPanel

def main():
    print("Octavia Phase1 Admin Shell")
    admin = AdminPanel()
    city = CityPanel()
    sarakt = SaraktPanel()

    while True:
        print("\nOptions")
        print("1) Mint batch of plots (admin)")
        print("2) Set ownership change fee (admin)")
        print("3) Inspect treasuries (admin)")
        print("4) List a plot for sale (city operator)")
        print("5) Buy plot from secondary (buyer)")
        print("6) Withdraw Sarakt funds (planet operator)")
        print("7) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            start = int(input("startId: "))
            count = int(input("count: "))
            area = int(input("area m2: "))
            to = input("to address: ")
            admin.mint_initial_plots(start, count, area, to)
        elif choice == "2":
            fee = float(input("ownership change fee (xBGL): "))
            admin.set_ownership_fee(fee)
        elif choice == "3":
            admin.inspect_treasuries()
        elif choice == "4":
            pid = int(input("plot id: "))
            price = float(input("price xBGL: "))
            city.list_secondary(pid, price)
        elif choice == "5":
            pid = int(input("plot id: "))
            city.buy_secondary(pid)
        elif choice == "6":
            to = input("to address: ")
            amt = float(input("amount xBGL: "))
            sarakt.withdraw_sarakt(to, amt)
        elif choice == "7":
            print("bye")
            sys.exit(0)
        else:
            print("invalid")

if __name__ == "__main__":
    main()
