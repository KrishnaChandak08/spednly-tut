#Description Create a Single Dummy Indian User in the Database

## Step 1: Analyze Database Schema
Read `database/db.py` to understand the `users` table schema and the implementation of the `get_db()` helper.

## Step 2: Write and Execute a Python Script
Create and run a Python script that completes the following steps:

1. **Generate a Realistic Indian User:**
   * **Name:** Create a realistic Indian first and last name using common Indian names across different regions.
   * **Email:** Derive the email from the generated name, appending a random 2-to-3 digit number suffix (e.g., `rahul.sharma91@gmail.com`).
   * **Password:** Use `"password123"` hashed securely with `werkzeug.security.generate_password_hash`.
   * **created_at:** Set to the current UTC datetime.

2. **Ensure Uniqueness:**
   * Check if the generated email already exists in the `users` table. 
   * If it exists, regenerate the name, email, and suffix until a unique email is found.

3. **Database Insertion:**
   * Insert the new user record into the database, utilizing the exact same `get_db()` context manager/pattern found in `database/db.py`.

4. **Output Confirmation:**
   * Upon successful insertion, print the following details of the created user to the console:
     * `id`
     * `name`
     * `email`
