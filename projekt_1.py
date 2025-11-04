import requests
import csv
import time
from functools import wraps

class DownloadError(Exception):
    pass
class NotFoundError(DownloadError):
    pass
class AccessDeniedError(DownloadError):
    pass

# ️ Dekorator logujący czas
def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f" Start: {func.__name__}")
        result = func(*args, **kwargs)
        end = time.time()
        print(f" Koniec: {func.__name__} (czas: {end - start:.2f} sekundy)")
        return result
    return wrapper

#  Funkcja pobierająca plik
def download_file(url: str, filename: str = "latest.txt") -> None:
    try:
        response = requests.get(url)
        if response.status_code == 404:
            raise NotFoundError(f"Plik nie został znaleziony: {url}")
        elif response.status_code == 403:
            raise AccessDeniedError(f"Brak dostępu do pliku: {url}")
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f" Plik został zapisany jako: {filename}")
    except NotFoundError as nf:
        print(f" Błąd 404: {nf} ")
    except AccessDeniedError as ad:
        print(f" Błąd 403: {ad} ")
    except requests.exceptions.RequestException as e:
        print(f"  Inny błąd pobierania: {e} ")

# Klasa ETL
class SimpleETL:
    def __init__(self, input_file: str):
        self.input_file = input_file

    def row_generator(self):
        with open(self.input_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

    @log_time
    def process(self):
        with open("values.csv", mode="w", newline='', encoding='utf-8') as val_out, \
             open("missing_values.csv", mode="w", newline='', encoding='utf-8') as miss_out:

            val_writer = csv.writer(val_out)
            miss_writer = csv.writer(miss_out)

            val_writer.writerow(["id", "sum", "mean"])
            miss_writer.writerow(["id", "missing_indexes"])

            for row in self.row_generator():
                row_id = row[0]
                values = row[1:]
                missing = [i + 1 for i, val in enumerate(values) if val.strip() == "-"]
                numeric_values = [float(val) for val in values if val.strip() != "-"]
                total = sum(numeric_values)
                mean = total / len(numeric_values) if numeric_values else 0.0
                val_writer.writerow([row_id, round(total, 2), round(mean, 2)])
                miss_writer.writerow([row_id, missing])

# Uruchomienie
if __name__ == "__main__":
    url = "https://oleksandr-fedoruk.com/wp-content/uploads/2025/10/sample.csv"
    download_file(url)
    etl = SimpleETL("latest.txt")
    etl.process()
