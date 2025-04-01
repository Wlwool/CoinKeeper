from aiogram.fsm.state import State, StatesGroup


class AddIncomeStates(StatesGroup):
    """Шаги для добавления дохода"""
    amount = State()
    category = State()
    description = State()

class AddExpenseStates(StatesGroup):
    """Шаги для добавления расхода"""
    amount = State()
    category = State()
    description = State()

class ChooseCategoryStates(StatesGroup):
    """Шаги для выбора категории"""
    pass