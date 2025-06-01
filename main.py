import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import csv
from datetime import datetime

class CowboyRideLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cowboy Ride Log App")

        self.create_widgets()
        self.load_existing_rides()

    def create_widgets(self):
        tk.Label(self.root, text="Date:").grid(row=0, column=0, sticky=tk.W)
        self.date_entry = DateEntry(self.root, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Cowboys (comma-separated):").grid(row=1, column=0, sticky=tk.W)
        self.cowboys_entry = tk.Entry(self.root)
        self.cowboys_entry.grid(row=1, column=1)

        tk.Label(self.root, text="From:").grid(row=2, column=0, sticky=tk.W)
        self.from_entry = tk.Entry(self.root)
        self.from_entry.grid(row=2, column=1)

        tk.Label(self.root, text="To:").grid(row=3, column=0, sticky=tk.W)
        self.to_entry = tk.Entry(self.root)
        self.to_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Drove to Start (Yes/No):").grid(row=4, column=0, sticky=tk.W)
        self.drove_entry = tk.Entry(self.root)
        self.drove_entry.grid(row=4, column=1)

        tk.Button(self.root, text="Add Ride", command=self.add_ride_entry).grid(row=5, columnspan=2)
        tk.Button(self.root, text="Generate Season Summary", command=self.generate_season_summary).grid(row=6, columnspan=2)

        tk.Label(self.root, text="Edit Ride by Date:").grid(row=7, column=0, sticky=tk.W)
        self.date_dropdown = ttk.Combobox(self.root, state="readonly")
        self.date_dropdown.grid(row=7, column=1)
        self.date_dropdown.bind("<<ComboboxSelected>>", self.populate_form_for_edit)

        tk.Button(self.root, text="Save Changes", command=self.save_changes).grid(row=8, columnspan=2)
        tk.Button(self.root, text="Delete Ride", command=self.delete_ride).grid(row=9, columnspan=2)

    def load_existing_rides(self):
        self.ride_log = []
        try:
            with open("cowboy_rides_log.csv", mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.ride_log.append(row)
            self.update_date_dropdown()
        except FileNotFoundError:
            pass

    def update_date_dropdown(self):
        dates = [ride["Date"] for ride in self.ride_log]
        self.date_dropdown['values'] = dates

    def populate_form_for_edit(self, event):
        selected_date = self.date_dropdown.get()
        for ride in self.ride_log:
            if ride["Date"] == selected_date:
                self.date_entry.set_date(ride["Date"])
                self.cowboys_entry.delete(0, tk.END)
                self.cowboys_entry.insert(0, ride["Cowboys"])
                self.from_entry.delete(0, tk.END)
                self.from_entry.insert(0, ride["From"])
                self.to_entry.delete(0, tk.END)
                self.to_entry.insert(0, ride["To"])
                self.drove_entry.delete(0, tk.END)
                self.drove_entry.insert(0, ride["Drove to Start"])
                break

    def add_ride_entry(self):
        date = self.date_entry.get()
        cowboys = self.cowboys_entry.get()
        from_location = self.from_entry.get()
        to_location = self.to_entry.get()
        drove_to_start = self.drove_entry.get()

        num_cowboys = len(cowboys.split(","))
        self.ride_log.append({
            "Date": date,
            "Cowboys": cowboys,
            "Number of Cowboys": num_cowboys,
            "From": from_location,
            "To": to_location,
            "Drove to Start": drove_to_start
        })

        self.save_to_csv()
        self.update_date_dropdown()

        self.date_entry.set_date(datetime.now())
        self.cowboys_entry.delete(0, tk.END)
        self.from_entry.delete(0, tk.END)
        self.to_entry.delete(0, tk.END)
        self.drove_entry.delete(0, tk.END)

        messagebox.showinfo("Ride Added", "Ride entry added successfully!")

    def save_changes(self):
        selected_date = self.date_dropdown.get()
        for ride in self.ride_log:
            if ride["Date"] == selected_date:
                ride["Date"] = self.date_entry.get()
                ride["Cowboys"] = self.cowboys_entry.get()
                ride["Number of Cowboys"] = len(self.cowboys_entry.get().split(","))
                ride["From"] = self.from_entry.get()
                ride["To"] = self.to_entry.get()
                ride["Drove to Start"] = self.drove_entry.get()
                break

        self.save_to_csv()
        self.update_date_dropdown()

        messagebox.showinfo("Changes Saved", "Ride entry updated successfully!")

    def delete_ride(self):
        selected_date = self.date_dropdown.get()
        if not selected_date:
            messagebox.showwarning("No Selection", "Please select a ride date to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the ride on {selected_date}?")
        if not confirm:
            return

        self.ride_log = [ride for ride in self.ride_log if ride["Date"] != selected_date]

        self.save_to_csv()
        self.update_date_dropdown()

        self.date_entry.set_date(datetime.now())
        self.cowboys_entry.delete(0, tk.END)
        self.from_entry.delete(0, tk.END)
        self.to_entry.delete(0, tk.END)
        self.drove_entry.delete(0, tk.END)

        messagebox.showinfo("Ride Deleted", "Ride entry deleted successfully!")

    def save_to_csv(self):
        with open("cowboy_rides_log.csv", mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Date", "Cowboys", "Number of Cowboys", "From", "To", "Drove to Start"])
            writer.writeheader()
            writer.writerows(self.ride_log)

    def generate_season_summary(self):
        total_days_rode = len(self.ride_log)
        total_days_drove = sum(1 for ride in self.ride_log if ride["Drove to Start"].lower() == "yes")

        cowboy_days = {}
        for ride in self.ride_log:
            cowboys = ride["Cowboys"].split(",")
            for cowboy in cowboys:
                cowboy = cowboy.strip()
                cowboy_days[cowboy] = cowboy_days.get(cowboy, 0) + 1

        summary_message = f"Total Days Rode: {total_days_rode}\nTotal Days Drove: {total_days_drove}\n\nDays Each Cowboy Rode:\n"
        for cowboy, days in cowboy_days.items():
            summary_message += f"{cowboy}: {days} days\n"

        messagebox.showinfo("Season Summary", summary_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = CowboyRideLogApp(root)
    root.mainloop()
