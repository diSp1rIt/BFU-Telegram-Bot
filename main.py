from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = '5721222678:AAEgbEjJenIUDfW-ILDrQ758-KoLnPu5wpQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# States -----------
class Schedule(StatesGroup):
    waiting_for_group = State()


class Login(StatesGroup):
    waiting_for_code = State()


class HeadMan(StatesGroup):
    menu = State()


class CreateGroup(StatesGroup):
    waiting_for_name = State()


class EditGroup(StatesGroup):
    waiting_for_group = State()
    waiting_for_weekday = State()
    waiting_for_subject = State()
# End states -------


subjects = [
    'Окно',
    'Дифференциальные уравнения',
    'Алгелра',
    'Прикладная алгебра',
    'Математический анализ',
    'Геометрия',
    'Философия',
    'БЖД',
    'Физ-ра',
    'Дискретная математика',
    'Физика',
    'Введение в специальность',
    'Теория чисел',
    'Английский язык',
    'Немецкий язык',
    'Комплексный анализ',
]

weekdays = [
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
]

groups = {
    'name_group_test': [
        ['комплан', 'дифуры', '', '', 'физра', ''],
        ['', '', 'Физра'] + [''] * 3,
        [''] * 6,
        [''] * 6,
        [''] * 6,
        [''] * 6,
    ]
}

users = {}


@dp.message_handler(commands=['test'], state='*')
async def test(message: types.Message, state: FSMContext):
    await message.answer(type(await state.get_state()))


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет\nЯ твой помощник - бот для расписания.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['schedule'], state='*')
async def schedule(message: types.Message, state: FSMContext):
    await state.update_data(prev_state=await state.get_state())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for key in groups.keys():
        keyboard.add(key)

    await state.set_state(Schedule.waiting_for_group.state)

    await message.answer('Выберете группу', reply_markup=keyboard)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    state_ = await state.get_state()
    if state_ is not None:
        if state_ != 'Schedule:waiting_for_group':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Создать группу')
            keyboard.add('Редактировать группу')
            await state.set_state(HeadMan.menu.state)
            await message.answer('Отмена', reply_markup=keyboard)
        else:
            await state.finish()
            await message.answer('Отмена', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['headman'])
async def headman(message: types.Message, state: FSMContext):

    await state.set_state(Login.waiting_for_code.state)
    await message.answer('Введите ключ доступа')


@dp.message_handler(state=Schedule.waiting_for_group)
async def schedule_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(data['prev_state'])

    group_name = message.text
    if group_name not in groups.keys():
        await message.answer('Используйте кнопки')
        return

    for i in range(len(groups[group_name])):
        ans = weekdays[i] + '\n\n' + '\n'.join([f'{j + 1}) ' + groups[group_name][i][j] for j in range(6)])
        await message.answer(ans, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Login.waiting_for_code)
async def key_handler(message: types.Message, state: FSMContext):
    if message.text != 'привет':
        await message.answer('Неверный ключ')
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Создать группу')
    keyboard.add('Редактировать группу')

    await state.set_state(HeadMan.menu.state)

    await message.answer('Вы успешно вошли как староста', reply_markup=keyboard)


@dp.message_handler(state=HeadMan.menu)
async def menu_handler(message: types.Message, state: FSMContext):
    if message.text.lower() == 'создать группу':
        await state.set_state(CreateGroup.waiting_for_name.state)

        await message.answer('Напишите название группы (направление_курс_№подгруппы)', reply_markup=types.ReplyKeyboardRemove())
    elif message.text.lower() == 'редактировать группу':
        await state.set_state(EditGroup.waiting_for_group.state)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for key in groups.keys():
            if message.chat.id in users.keys() and key in users[message.chat.id]:
                keyboard.add(key)
        if len(keyboard.keyboard) == 0:
            await message.answer('У вас нет групп')
            return
        await message.answer('Выберете группу', reply_markup=keyboard)


@dp.message_handler(state=CreateGroup.waiting_for_name)
async def create_group_handler(message: types.Message, state: FSMContext):
    group_name = message.text
    groups[group_name] = [[''] * 7 for _ in range(6)]
    if message.chat.id not in users.keys():
        users[message.chat.id] = [group_name]
    else:
        users[message.chat.id].append(group_name)

    await state.set_state(HeadMan.menu.state)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Создать группу')
    keyboard.add('Редактировать группу')

    await message.answer(f'Вы создали группу {group_name}', reply_markup=keyboard)


@dp.message_handler(state=EditGroup.waiting_for_group)
async def select_group_for_edit_handler(message: types.Message, state: FSMContext):
    group_name = message.text
    if group_name not in groups.keys():
        await message.answer('Используйте кнопки')
        return

    await state.update_data(group=group_name)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for weekday in weekdays:
        keyboard.add(weekday)

    await state.set_state(EditGroup.waiting_for_weekday.state)

    await message.answer('Выберите день недели', reply_markup=keyboard)


@dp.message_handler(state=EditGroup.waiting_for_weekday)
async def select_weekday_handler(message: types.Message, state: FSMContext):
    weekday = message.text
    if weekday not in weekdays:
        await message.answer('Используйте кнопки')
        return

    await state.update_data(weekday=weekdays.index(weekday))
    await state.update_data(lesson=0)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subjects:
        keyboard.add(subject)

    await state.set_state(EditGroup.waiting_for_subject.state)

    await message.answer('Пара 1\nВыберите предмет или напишите его сами', reply_markup=keyboard)


@dp.message_handler(state=EditGroup.waiting_for_subject)
async def select_subject_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subject = message.text

    if subject == 'Окно':
        subject = ''

    groups[data['group']][data['weekday']][data['lesson']] = subject

    if data['lesson'] + 1 >= 6:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for weekday in weekdays:
            keyboard.add(weekday)

        await state.set_state(EditGroup.waiting_for_weekday.state)

        await message.answer(f'Расписание на {weekdays[data["weekday"]]} составлено\n Выберите день недели', reply_markup=keyboard)
        return

    await state.update_data(lesson=data['lesson'] + 1)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subjects:
        keyboard.add(subject)

    await state.set_state(EditGroup.waiting_for_subject.state)

    await message.answer(f'Пара {data["lesson"] + 2}\nВыберите предмет или напишите его сами', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)



