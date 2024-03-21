import os

file_path = r'C:\Users\liyihang\PycharmProjects\1\tutorial\Chapter 1 '

try:
    os.remove(file_path)
    print(f"File '{file_path}' deleted successfully.")
except OSError as e:
    print(f"Error: {file_path} : {e.strerror}")
