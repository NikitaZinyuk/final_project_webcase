from django import forms
from .models import Messages, UserProfile
from django.contrib.auth.models import User

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'photo', 'phonenumber')

class NewMessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['title', 'order', 'description', 'mark', 'channel']

# class Messages(models.Model):
#     title = models.CharField('Заголовок сообщения', max_length=100,
#                              help_text='Например: Разговор с менеджером компании')
#     order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True, verbose_name='Заказ')
#     description = models.TextField('Вид обращение, комментарий', max_length=1000,
#                                    help_text='Разговор по телефону с менеджером. Сказали, что денег больше не дадут')
#     MARK = (
#         ('g', 'Хорошо'),
#         ('b', 'Плохо'),
#     )
#     mark = models.CharField('Оценка обращения', max_length=1, choices=MARK, blank=True, default='g',
#                             help_text='Оценка связи с компанией')
#     manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     pub_date = models.DateTimeField('Дата публикации сообщения', default=datetime.now())
