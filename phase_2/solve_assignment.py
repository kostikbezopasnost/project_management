from itertools import product
from pathlib import Path

from openpyxl import load_workbook


def read_estimates():
    path = Path(__file__).with_name("predpochteniya uchastnikov.xlsx")
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook["Оценки экспертов"]
        rows = sheet.iter_rows(min_row=4, max_col=6, values_only=True)
        _, _, _, *participants = next(rows)
        tasks = [row for row in rows if row[0] is not None]
    finally:
        workbook.close()

    if not tasks or any(not name for name in participants):
        raise ValueError("В таблице должны быть задачи и имена участников.")

    for number, title, hours, *scores in tasks:
        if not title or not isinstance(hours, (int, float)) or hours <= 0:
            raise ValueError(f"Для задачи {number} нужны название и трудозатраты.")
        if any(not isinstance(score, int) or not 1 <= score <= 5 for score in scores):
            raise ValueError(f"Для задачи {number} нужны целые баллы от 1 до 5.")

    return participants, tasks


def main():
    participants, tasks = read_estimates()
    participant_indices = range(len(participants))
    best_rank = (float("inf"), float("inf"))
    best_assignments = []
    checked = 0

    for assignment in product(participant_indices, repeat=len(tasks)):
        checked += 1
        loads = [0] * len(participants)
        total_score = 0
        for (_, _, hours, *scores), participant in zip(tasks, assignment):
            loads[participant] += hours
            total_score += scores[participant]

        # Python compares tuples in order. Negating the score turns maximization into minimization.
        rank = (-total_score, max(loads))
        if rank < best_rank:
            best_rank = rank
            best_assignments.clear()
        if rank == best_rank:
            best_assignments.append((assignment, loads))

    print(f"Проверено вариантов: {checked}")
    print(f"Оптимальных вариантов: {len(best_assignments)}")
    print(f"Сумма баллов: {-best_rank[0]}. Максимальная нагрузка: {best_rank[1]:g} ч.")
    for index, (assignment, loads) in enumerate(best_assignments, start=1):
        print(f"\nВариант {index}")
        for (number, title, hours, *scores), participant in zip(tasks, assignment):
            print(f"{number}. {title} | {participants[participant]} | {hours:g} ч | {scores[participant]}")
        for name, hours in zip(participants, loads):
            print(f"{name}: {hours:g} ч")


if __name__ == "__main__":
    main()
