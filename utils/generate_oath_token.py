import gspread

gc = gspread.oauth(
    credentials_filename="config/credentials.json",           # your OAuth client file
    authorized_user_filename="config/token.json"              # where the token will be saved
)