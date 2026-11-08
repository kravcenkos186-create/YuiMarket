import py_compile
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "yui_src.py"
TARGET = HERE / "main.py"


def build(keep, drop):
    out, skipping = [], False
    for n, line in enumerate(SRC.read_text("utf-8").splitlines(keepends=True), 1):
        s = line.strip()
        if s == f"# <{drop}>":
            skipping = True
            continue
        if s == f"# </{drop}>":
            skipping = False
            continue
        if s in (f"# <{keep}>", f"# </{keep}>"):
            continue
        if not skipping:
            out.append(line)
    if skipping:
        sys.exit(f"Помилка: не закритий блок {drop}")
    return "".join(out)


def main():
    # Збираємо чистий комерційний файл main.py для продажу бєти пацанам
    target = TARGET
    target.write_text(build("SALE", "PERSONAL"), "utf-8")
    py_compile.compile(str(target), doraise=True)
    print(f"OK  {target}  ({len(target.read_text('utf-8').splitlines())} рядків)")
    print("📦 Комерційний файл [main.py] успішно згенеровано для продажу під твій фіолетовий арт!")


if __name__ == "__main__":
    main()
