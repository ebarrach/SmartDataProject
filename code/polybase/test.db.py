import bcrypt

hash = b"$2b$12$S1l8Qb0/6wg6dqd2Fu1.U.T6MhTcK7RbfwMbqxnJ5/7xZP1lyJq02"
motdepasse = b"polybase123"

print(bcrypt.checkpw(motdepasse, hash))
