import random
import sys
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(__file__))
from database.db import get_db

FIRST_NAMES = [
    "Aarav", "Rohit", "Vikram", "Arjun", "Karan", "Suresh", "Rajesh", "Amit",
    "Priya", "Neha", "Anjali", "Pooja", "Divya", "Sunita", "Meera", "Kavya",
    "Ravi", "Sunil", "Deepak", "Nikhil", "Aditya", "Sanjay", "Manish", "Rahul",
    "Ananya", "Shreya", "Lakshmi", "Nandini", "Pallavi", "Isha",
]

LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Patel", "Gupta", "Mehta", "Joshi", "Mishra",
    "Nair", "Pillai", "Reddy", "Rao", "Iyer", "Menon", "Krishnan", "Bhat",
    "Chatterjee", "Banerjee", "Das", "Bose", "Malhotra", "Kapoor", "Khanna", "Chopra",
]


def generate_user():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    suffix = random.randint(10, 999)
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    return name, email


def seed_user():
    conn = get_db()
    password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for _ in range(100):
        name, email = generate_user()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, created_at),
            )
            conn.commit()
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            print(f"User created successfully:")
            print(f"  id:    {user_id}")
            print(f"  name:  {name}")
            print(f"  email: {email}")
            conn.close()
            return

    conn.close()
    print("Failed to generate a unique email after 100 attempts.")
    sys.exit(1)


if __name__ == "__main__":
    seed_user()
