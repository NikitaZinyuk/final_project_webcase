from django.contrib import admin
from .models import Sorts, PhonenumbersComp, UserProfile, PhonenumbersSupp, Emails, Suppliers, Messages, Companies, Orders, Tasks
from django.utils.safestring import mark_safe

admin.site.register(Sorts)
admin.site.register(PhonenumbersComp)
admin.site.register(PhonenumbersSupp)
admin.site.register(Emails)
admin.site.register(UserProfile)

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    '''
    Класс для отображения панели с детальной информацией о заданиях для персонала
    Показывает название задания и всех исполнителей
    '''
    list_display = ['name', 'display_excutors']

class OrdersInline(admin.TabularInline):
    """
    Инлойновый класс для отобажения заказов при просмотре компаний.
    """
    model = Orders

class PhoneInline(admin.TabularInline):
    """
    Инлайновый класс для показа номеров телефонов компании
    """
    model = PhonenumbersComp

class EmailInline(admin.TabularInline):
    """
    Инлайновый класс для показа емейлов компании
    """
    model = Emails


class PhoneSupInline(admin.TabularInline):
    """
    Инлайновый класс для показа номеров телефона поставщика
    """
    model = PhonenumbersSupp

@admin.register(Suppliers)
class SuppliersAdmin(admin.ModelAdmin):
    """
    Класс для отображения панели при просмотре списка поставщиков
    ФИ, количество меда и сорт
    Фильтрация по количеству и сорту
    Инлайново показывается телефоны
    """
    list_display = ['first_name', 'last_name', 'amount', 'sort']
    list_filter = ['amount', 'sort']
    inlines = [PhoneSupInline]

@admin.register(Companies)
class CompaniesAdmin(admin.ModelAdmin):
    """
    Класс для отображения списка компаний
    Отображается Название компании, менеджер
    Инлайново отображается Телефоны, емейлы, заказы
    """
    list_display =['name', 'manager']
    inlines = [PhoneInline, EmailInline, OrdersInline]

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    """
    Для отображения сообщений
    Отображается заголовок, оценка, заказ, менеджер
    Фильтрация по менеджеру и оценке
    """
    list_display = ['title', 'mark', 'order', 'manager']
    list_filter = ['manager', 'mark']


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    """
    Заказы
    Имя, дата начала, дата окончания, количество меда, сорт
    Фильтрация по сорту и количеству
    """
    list_display = ['name', 'date_of_start', 'date_of_end', 'amount', 'sort']
    list_filter = ['sort', 'amount']

class UserProfileAdmin(admin.ModelAdmin):
    """
    Профиль пользователя
    Показывает логин пользователя, фото
    """
    list_display = ('user', 'get_photo')
    fields = ('user')

    def get_photo(self, obj):
        """
        Показывает фото в админке
        :param obj: пользователь, берет ссылку на его фото.
        :return: фото
        """
        return mark_safe(f'<img src={obj.photo.url} width="50" height="60')
    get_photo.short_description = 'Фото'

# Register your models here.
