from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from datetime import date
"""
В основном своем фунция стр возвращает либо название объекта, либо сам объект(Номер телефона, емейл). Класс мета
содержит название модели в множественном и единственном числе
"""


class Sorts(models.Model):
    """
    Сорты
    Имеет называние.
    """
    name = models.CharField('Название сорта', max_length=50, help_text='Название сорта меда')

    def __str__(self):
        """
        :return: Возвращает название сорта в отображении
        """
        return self.name

    class Meta:
        verbose_name = 'Сорт меда' # в единственном числе
        verbose_name_plural = 'Сорта меда' # в множественном


class Emails(models.Model):
    """
    Емейлы.
    Сам емейл
    Фореинкей компании
    """
    email = models.EmailField('Адрес электронной почты', max_length=254, help_text='Электронная почта')
    company = models.ForeignKey('Companies', on_delete=models.CASCADE, null=True,
                                help_text='Электронный адрес компании', verbose_name='Электронный адрес')

    def __str__(self):
        """
        :return: возвращает записанный емейл в отображении
        """
        return self.email

    class Meta:
        verbose_name = 'Электронный адрес'
        verbose_name_plural = 'Электронные адреса'


class PhonenumbersComp(models.Model):
    """
    Номера телефонов компании
    Сам номер.
    Компания фореинкей
    """
    number = models.CharField('Номер телефона', max_length=30, help_text='Номер телефона')
    company = models.ForeignKey('Companies', on_delete=models.CASCADE, null=True,
                                help_text='Номер телефона компании', verbose_name='Номер телефона')

    def __str__(self):
        """
        Класс мета в единственном и множественном числе
        Функция стр тоже самое как и везде
        :return: вовзращает номер телефона в отображении
        """
        return self.number

    class Meta:
        verbose_name = 'Номер телефона компании'
        verbose_name_plural = 'Номера телефона компаний'


class PhonenumbersSupp(models.Model):
    """
    Номера телефонов поставщиков
    Тоже самое что и для компании
    """
    number = models.CharField('Номер телефона', max_length=30, help_text='Номер телефона')
    supplier = models.ForeignKey('Suppliers', on_delete=models.CASCADE, null=True,
                                 help_text='Номер телефона Поставщика', verbose_name='Номер телефона')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Номер телефона поставщика'
        verbose_name_plural = 'Номера телефона поставщиков'


class Companies(models.Model):
    """
    Модель компаний.
    Название компании
    Менеджер
    Описание
    Дата публикации(дата создании записи используется текущая(в день когда создается запись), дата изменения тоже самое))
    Адрес
    """
    name = models.CharField('Название компании', max_length=200, help_text='Название компании')
    manager = models.CharField('Контактное лицо', max_length=200, help_text='Контактное лицо')
    description = models.TextField('Краткое описание компании', max_length=1000, help_text='Краткое описание компании')
    pub_date = models.DateField('Дата записи', default=timezone.now, null=True, blank=True, help_text='Дата записи')
    change_date = models.DateField('Дата изменения записи', default=timezone.now, null=True, blank=True,
                                   help_text='Дата изменения записи')
    adress = models.CharField('Адрес доставки партии меда', max_length=100, help_text='Адрес доставки партии меда')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        :return: Ссылку на детальный просмотр компании. Праймери кей(айди) в качестве части ссылки.
        """
        return reverse('company-detail', args=[str(self.id)])

    class Meta:
        """
        Единсвтенное, множественное название
        пермишины для просмотра
        Вывод в алфавитном порядке
        """
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        permissions = (("can_view_list_of_companies", "Can view list of companies"),)
        ordering = ['name']

    def display_phonenumbers(self):
        """
        :return: выводит все номера компании
        """
        return ', '.join([number.number for number in self.phonenumbers.all()[:3]])

    display_phonenumbers.short_description = 'Номера телефонов'

    def display_emails(self):
        """
        :return: Выводит все емейлы
        """
        return ', '.join([email.email for email in self.emails.all()[:3]])

    display_emails.short_description = 'Адреса электронной почты'


class Suppliers(models.Model):
    """
    Модель поставщиков
    ФИО
    Сорт
    Количество меда
    Цена, которую обещали поставщику
    Статус анализа(выбор из СТАТУС АНАЛИЗА)
    Дата вывоза меда у поставщика
    """
    first_name = models.CharField('Имя поставщика', max_length=50, help_text='Имя')
    last_name = models.CharField('Фамилия поставщика', max_length=50, help_text='Фамилия')
    patronymic = models.CharField('Отчество', max_length=50, help_text='Отчество')
    sort = models.CharField('Название сорта меда', max_length=200, null=True, blank=True, help_text='Сорт')
    amount = models.IntegerField('Количество меда', help_text='В килограммах')
    price = models.IntegerField('Цена за килограмм', help_text='В гривнах')
    STATUS_OF_ANALYSIS = (
        ('n', 'Не взят'),
        ('y', 'Взяли'),
        ('c', 'Проверяется в лаборатории'),
        ('r', 'Готов, но результаты еще не пришли'),
        ('w', 'С антибиотиком'),
        ('b', 'Без антибиотика'),
    )  # n = no, y = yes, c = check, r = ready, w = with, b = without(потому что w уже занята)

    status_of_analysis = models.CharField('Статус Анализа', max_length=1, choices=STATUS_OF_ANALYSIS, blank=True,
                                          default='n',
                                          help_text='Выбирете статус анализа')
    date_of_export = models.DateField(null=True, blank=True, help_text='Дата вывоза меда')

    def __str__(self):
        """
        ФИ поставщика, количество меда. С помощью ф строки.
        :return:
        """
        return f'{self.first_name} {self.last_name}. Количество меда - {self.amount}кг'

    class Meta:
        """
        Пермишины на просмотр. Ед и мн названия.
        """
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        permissions = (("can_view_list_of_suppliers", "Can view list of suppliers"),)

    def display_phonenumbers(self):
        """
        :return: все номера телефонов
        """
        return ', '.join([number.number for number in self.phonenumber.all()[:3]])

    display_phonenumbers.short_description = 'Номера телефонов'

    def get_absolute_url(self):
        """
        :return: ссылка на просмотр детальной информации. Айди как часть ссылки
        """
        return reverse('suppliers-detail', args=[str(self.id)])


class Orders(models.Model):
    """
    Модель заказов.
    Название заказа
    Дата начала
    Конца
    Короткое описание
    Количество
    Цена
    Компания форейнкей
    Поставщики мени то мени(может быть несколько поставщиков задействовано в заказе
    Стату выполнения(выбор из ВЫПОЛНЕНИЯ)
    """
    name = models.CharField('Название заказа', max_length=200, help_text='Например: Заказ на 2000кг')
    date_of_start = models.DateField('Дата начала выполнения заказа', null=True, blank=True)
    date_of_end = models.DateField('Дата окончания выполнения заказа', null=True, blank=True)
    short_description = models.TextField('Краткое описание', max_length=3000,
                                         help_text='Например: Компания оформила заказ, уже оплатила(не оплатила) и т.д.')
    amount = models.IntegerField('Количество меда', help_text='В килограммах')
    sort = models.CharField('Название сорта меда', max_length=200, null=True, blank=True, help_text='Сорт')
    price = models.IntegerField('Цена за килограмм', help_text='В гривнах')
    company = models.ForeignKey('Companies', on_delete=models.CASCADE, null=True,
                                help_text='Компания, для которой выполняется заказ', verbose_name='Выберите компанию')
    suppliers = models.ManyToManyField(Suppliers, blank=True,
                                       help_text='Выберите поставщиков', verbose_name='Поставщики')
    DONE = (
        ('d', 'Выполнено'),
        ('n', 'Не выполнено'),
    )
    done = models.CharField('Выполнение', max_length=1, choices=DONE, blank=True, default='n',
                            help_text='Задание выполнено или нет')

    class Meta:
        """
        Отдельные пермишины. Ед и мн названия
        """
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        permissions = (("can_view_list_of_orders", "Can view list of orders"),)

    def __str__(self):
        """
        :return: заголовок заказа в отображении
        """
        return self.name

    def summary(self):
        """
        Количетсво умножается на цену
        :return: Возвращает сумму заказа
        """
        return int(self.amount)*int(self.price)

    def get_absolute_url(self):
        """
        :return: ссылка на детальный просмотр заказа
        """
        return reverse('orders-detail', args=[str(self.id)])




class Messages(models.Model):
    """
    Модель сообщений
    Заголовок
    Заказ фореинкей
    Текст сообщения
    Оценка(Выбор и ОЦЕНКА)
    Канал обращения(Выбор из КАНАЛ, исходя из задания)
    Менеджер фореинкей юзер, который оставлял сообщение
    Дата публикации
    """
    title = models.CharField('Заголовок сообщения', max_length=100,
                             help_text='Например: Разговор с менеджером компании.')
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True, verbose_name='Заказ')
    description = models.TextField('Вид обращение, комментарий', max_length=1000,
                                   help_text='Например: Разговор по телефону с менеджером. Сказали, что денег больше не дадут.')
    MARK = (
        ('g', 'Хорошо'),
        ('b', 'Плохо'),
    )
    mark = models.CharField('Оценка обращения', max_length=1, choices=MARK, blank=True, default='g',
                            help_text='Оценка связи с компанией')
    CHANNEL = (
        ('z', 'Заявка'),
        ('l', 'Письмо'),
        ('s', 'Сайт'),
        ('i', 'Инициатива компании'),
        ('p', 'Звонок'),
    )
    channel = models.CharField('Канал обращения', max_length=1, choices=CHANNEL, blank=True, default='')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pub_date = models.DateTimeField('Дата публикации сообщения', default=timezone.now)

    def __str__(self):
        """
        :return: заголовок сообщения
        """
        return self.title

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = (("can_view_list_of_messages", "Can view list of messages"),)

    def get_absolute_url(self):
        """
        :return: ссылка на просмотр детальной информации сообщения
        """
        return reverse('messages-detail', args=[str(self.id)])

    def new_message(self):
        """
        :return: Проверка новое сообщение или нет. Если от текущего времени не прошли сутки от даты публикации вовзращает Тру
        """
        if self.pub_date >= timezone.now() - datetime.timedelta(days=1):
            return True
        return False


class Tasks(models.Model):
    """
    Модель заданий
    Название задания
    Исполнители мени ту мени юзер(может быть несколько)
    Само задание с детальныи описанием
    Дата публикации
    Срок до которого нужно выполнить
    Статус выполнения(Выбор из ВЫПОЛНЕНО)
    """
    name = models.CharField('Название задания', max_length=250, help_text='Задание для персонала')
    excutors = models.ManyToManyField(User,
                                      help_text='Выберите исполнителей', verbose_name='Исполнители')
    task = models.TextField('Задание', max_length=3000)
    pub_date = models.DateField('Дата выдачи задания', null=True, blank=True, default=timezone.now)
    end_date = models.DateField('Дата окончания задания', null=True, blank=True)
    DONE = (
        ('d', 'Выполнено'),
        ('n', 'Не выполнено'),
    )
    done = models.CharField('Выполнение', max_length=1, choices=DONE, blank=True, default='n',
                            help_text='Задание выполнено или нет')

    def __str__(self):
        """
        :return: Возвращает название задания в отображении
        """
        return self.name

    class Meta:
        """
        Пермишионы. Ед и мн названия
        """
        verbose_name = 'Задание для персонала'
        verbose_name_plural = 'Задания для персонала'
        permissions = (('can_set_as_done', 'Can set as done'), ('can_view_my_tasks', 'Can view my tasks'),)

    def display_excutors(self):
        """
        :return: список всех исполнителей заадния.
        """
        return ', '.join([excutor.first_name for excutor in self.excutors.all()[:3]])

    def get_absolute_url(self):
        """
        :return: ссылка на просмотр задания.
        """
        return reverse('task-detail', args=[str(self.id)])


class UserProfile(models.Model):
    """
    Профиль пользователя
    Пользователь фореинкей юзер
    Фото
    Телефон
    Дата рождения
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(verbose_name='Фото профиля', upload_to='users/%Y/%m/%d', null=True, blank=True)
    phonenumber = models.CharField('Номер пользователя', max_length=10, null=True, blank=True)
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def get_absolute_url(self):
        """
        :return: ссылка на профиль пользователя.
        """
        return reverse('profile', args=[str(self.id)])
