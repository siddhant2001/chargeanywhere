# ChargeAnyWhere

## Endpoints documentation:
1) /register_user and /register_owner: Send a POST request in JSON format. The body should be a dictionary. The keys of these dictionaries are listed in models.py by the User class and Owner class. Returns id.
2) /login_user and /register_owner: Send a JSON POST request with "email" and "password" fields. Return status will be 200 and payload will have a user_id field in case of success.