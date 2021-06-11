# PasswordManager

A password manager using PostgreSQL and md5, fernet symmetric encryption. 

## Usage
Download postgres locally, and then proceed to launch PassManager through a virtual environment. In windows, you have to cd into pass and then run "pass\Scripts\activate".
Then you can type python db.py to run the program for the first time. 
If the program malfunctions, the first fix would be to turn off password access in postgres through the pg_hba file in programfiles\postgreSql\13\data directory. This can be done by changing "Method" in the bottom to "trust" instead of scram or md5. 

usage requires the following dependencies:
  * Psycopg2 for connecting with Postgres
  * cryptography for encrypting passwords
  * stdiomask to mask input for Password (Not yet implemented for practicality of development)
  * All other dependencies were already included with Python3

## Future features
  * Password Recovery
  * Tkinter GUI

## Collaboration
All feedback and support is appreciated. 


## License
[MIT](https://choosealicense.com/licenses/mit/)
