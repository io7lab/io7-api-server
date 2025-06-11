
The io7 IOT platform is desinged to have only one admin user. Hence the API entry point /users/signup can be executed just once when there is no admin user is setup.

And this is the emergency procedure to reset the admin user.

1. remove data/db/users.json
2. restart io7api(docker restart io7api)
3. run this API with the email and password modified
```
curl -X POST "http://localhost:2009/users/signup" \
-H 'accept: application/json' -H 'Content-Type: application/json' \
-d '{ "username" : "API User", "email" : "io7@io7lab.com", "password" : "strong!!!" }'
```
