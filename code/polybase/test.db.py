import bcrypt

motdepasse = b"admin1234"

# Générer le hash à partir du mot de passe
hash = bcrypt.hashpw(motdepasse, bcrypt.gensalt())

# Afficher le hash
print("Hash généré :", hash.decode())

# Vérifier le mot de passe avec le hash
print("Vérification mot de passe :", bcrypt.checkpw(motdepasse, hash))


hash = b"$2b$12$ejEmsLAepn0dkygqIfgX8.hXr8G8AIwozn6yzVRPdQ2PbqCrHBwKe"
motdepasse = b"admin1234"

print(bcrypt.checkpw(motdepasse, hash))
