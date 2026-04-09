import telebot
from math import factorial

TOKEN = "8792259827:AAEQfAEMHyF1HwBHd5WZrigYdR-2u0SuLa4"
bot = telebot.TeleBot(TOKEN)

user_data = {}

# =========================
# ЛОГИКА
# =========================

def Alpha(l, m):
    return l / m


def Potk(l, n, m):
    n = int(n)

    if n == 0:
        return 1

    s = 1
    for i in range(1, n + 1):
        s += (Alpha(l, m) ** n) / factorial(i)

    return round(((Alpha(l, m) ** n) / factorial(n)) / s, 3)


def Pgen(p1, p2, p3, l1, l2, l3):
    return round(l1*p1 + l2*p2 + l3*p3, 3)


def calculate_verbose(matrix1, matrix2, mu):
    Pg = [[], [], []]
    text = ""

    for i in range(3):
        for j in range(3):
            text += f"A{i+1} B{j+1}\n"

            Po = []

            for k in range(3):
                l = matrix1[i][k]
                n = int(matrix2[j][k])

                p = Potk(l, n, mu)
                Po.append(p)

                text += f"Alpha {l}, n {n}, Pотк {p}\n"

            pgen = Pgen(
                Po[0], Po[1], Po[2],
                matrix1[i][0], matrix1[i][1], matrix1[i][2]
            )

            Pg[i].append(pgen)

            text += f"Pобщ {pgen}\n\n"

        text += "----------\n\n"

    # ===== Таблица =====
    text += "     B1     B2     B3    \n"

    for i in range(3):
        text += f"A{i+1} |"
        for val in Pg[i]:
            text += f"{val:.3f}  "
        text = text.rstrip()
        text += "|\n"

    return text


# =========================
# ПАРСИНГ
# =========================

def parse_matrix(text, as_int=False):
    try:
        rows = text.split(";")

        if as_int:
            matrix = [list(map(int, row.strip().split())) for row in rows]
        else:
            matrix = [list(map(float, row.strip().split())) for row in rows]

        if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
            return None

        return matrix
    except:
        return None


# =========================
# ОБРАБОТЧИКИ
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    bot.send_message(
        message.chat.id,
        "Введи первую матрицу (вещественные числа)\n"
        "Пример:\n0.3 0.4 0.3; 0.4 0.4 0.2; 0.5 0.3 0.2"
    )


# --- MATRIX A (float) ---
@bot.message_handler(func=lambda m: m.chat.id in user_data and "A" not in user_data[m.chat.id])
def get_matrix_a(message):
    matrix = parse_matrix(message.text)

    if matrix is None:
        bot.send_message(message.chat.id, "❌ Ошибка! Введи матрицу 3x3 (вещественные числа).")
        return

    user_data[message.chat.id]["A"] = matrix
    bot.send_message(
        message.chat.id,
        "Теперь введи вторую матрицу (целые числа)\n"
        "Пример:\n2 1 1; 2 2 0; 1 2 1"
    )


# --- MATRIX B (int) ---
@bot.message_handler(func=lambda m: m.chat.id in user_data and "B" not in user_data[m.chat.id])
def get_matrix_b(message):
    matrix = parse_matrix(message.text, as_int=True)

    if matrix is None:
        bot.send_message(message.chat.id, "❌ Ошибка! Введи матрицу 3x3 из целых чисел.")
        return

    user_data[message.chat.id]["B"] = matrix
    bot.send_message(message.chat.id, "Теперь введи mu (например 0.3)")


# --- MU ---
@bot.message_handler(func=lambda m: m.chat.id in user_data and "mu" not in user_data[m.chat.id])
def get_mu(message):
    try:
        mu = float(message.text)
        if mu == 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ Введите корректное число (mu ≠ 0)")
        return

    user_data[message.chat.id]["mu"] = mu

    data = user_data[message.chat.id]

    result_text = calculate_verbose(
        data["A"], data["B"], data["mu"]
    )

    # делим сообщение (ограничение Telegram)
    for i in range(0, len(result_text), 4000):
        bot.send_message(message.chat.id, result_text[i:i+4000])

    user_data.pop(message.chat.id)


# =========================
# ЗАПУСК
# =========================

print("Бот запущен...")
bot.polling(none_stop=True)