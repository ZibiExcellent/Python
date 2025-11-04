# Ćwiczenia praktyczne 1 –eksperymenty z kontekstem

# 1. Klasa Logger — używana w bloku with do logowania wejścia i wyjścia
class Logger:
    def __enter__(self):
        print("Start sekcji logowania")  # Wypisuje komunikat przy wejściu do bloku with
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Koniec sekcji logowania")  # Wypisuje komunikat przy wyjściu z bloku with


# 2. Klasa FileWriter — zarządza zapisem do pliku w kontekście with
class FileWriter:
    def __init__(self, filepath):
        self.filepath = filepath  # Ścieżka do pliku
        self.file = None          # Uchwyt do pliku

    def __enter__(self):
        self.file = open(self.filepath, 'w', encoding='utf-8')  # Otwiera plik do zapisu
        return self.file  # Zwraca uchwyt do pliku

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()  # Zamyka plik niezależnie od błędu
        if exc_type:
            print(f"Błąd podczas zapisu: {exc_val}")  # Wypisuje komunikat o błędzie
        return False  # Nie tłumi wyjątku — program się zatrzyma


# 3. Klasa SafeDivision — bezpieczne dzielenie z tłumieniem błędu dzielenia przez zero
class SafeDivision:
    def __enter__(self):
        return self  # Zwraca siebie

    def divide(self, a, b):
        return a / b  # Próbuje wykonać dzielenie

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == ZeroDivisionError:
            print("Nie można dzielić przez zero")  # Tłumi tylko ZeroDivisionError
            return True  # Tłumi wyjątek
        return False  # Inne wyjątki nie są tłumione


# === TESTY DZIAŁANIA KLAS ===

# Test Loggera
with Logger():
    print("Wewnątrz bloku logowania")  # Wypisuje coś w środku

# Test FileWriter — zapis bez błędu
try:
    with FileWriter("test_output.txt") as f:
        f.write("To jest testowy zapis do pliku.\n")  # Zapisuje tekst do pliku
except Exception as e:
    print(f"Wyjątek z FileWriter: {e}")

# Test FileWriter — zapis z błędem (np. do katalogu zamiast pliku)
try:
    with FileWriter("C:/Windows") as f:  # Zakładamy, że to nie jest plik
        f.write("To się nie uda.\n")
except Exception as e:
    print(f"Wyjątek z FileWriter: {e}")  # Wyjątek nie jest tłumiony

# Test SafeDivision — poprawne dzielenie
with SafeDivision() as sd:
    print("Wynik dzielenia 10 / 2 =", sd.divide(10, 2))

# Test SafeDivision — dzielenie przez zero
with SafeDivision() as sd:
    print("Wynik dzielenia 5 / 0 =", sd.divide(5, 0))  # ZeroDivisionError zostanie stłumiony
