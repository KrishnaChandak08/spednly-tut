---
description: Seed realistic dummy expenses for a specific user over a given time range
arguments:
  - name: user_id
    description: The ID of the user to assign expenses to
    required: true
  - name: count
    description: Total number of expenses to generate
    required: true
  - name: months
    description: How many past months to spread the expenses across
    required: true
---

# Task: Seed Realistic Dummy Expenses for a User

## Step 1: Parse and Validate Arguments
Extract the runtime arguments provided to the command:
* `user_id` (Integer)
* `count` (Integer)
* `months` (Integer)

If any argument is missing, not a valid integer, or malformed, halt execution immediately and print:
`Usage: /seed-expenses <user_id> <count> <months>`
`Example: /seed-expenses 1 50 6`

## Step 2: Verify User Existence
Read `database/db.py` to identify the database connection setup. Before generating any expense records, check the `users` table. Verify that a user with the provided `user_id` exists. If no matching user is found, halt execution and print:
`No user found with id <user_id>.`

## Step 3: Generate and Insert Expenses
Write and execute a temporary Python script that implements the following generation logic:

1. **Date Distribution:** Randomly spread the timestamps of the generated expenses over the past `<months>` specified, going backward from the current date.
2. **Categories and Realistic Pricing (in ₹):**
   * **Food:** 50 - 800 (Most common category frequency)
   * **Transport:** 20 - 500
   * **Bills:** 200 - 3,000
   * **Health:** 100 - 2,000 (Least common category frequency)
   * **Entertainment:** 100 - 1,500 (Least common category frequency)
   * **Shopping:** 200 - 5,000
   * **Other:** 50 - 1,000
3. **Descriptions:** Use realistic localized descriptions suitable for an Indian context (e.g., "Swiggy order", "Auto fare", "Electricity Bill", "Zomato", "Metro recharge").
4. **Database Integrity Rules:**
   * Inherit the connection configuration directly from `database/db.py` (do not hardcode the filename or path string).
   * Enforce **parameterized queries** for all SQL operations to prevent syntax bugs or string escaping issues.
   * Wrap the bulk insertion process inside a single atomic transaction. If any individual insertion fails, roll back the entire operational block cleanly.

## Step 4: Print Confirmation Output
Upon a successful transaction commit, print a summary detailing:
* Total number of expenses successfully inserted.
* The exact historical date range spanning the generated records.
* A printed text sample layout showing 5 of the newly created expense records.