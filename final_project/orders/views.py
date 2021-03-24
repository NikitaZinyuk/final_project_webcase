from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import generic
from .models import Companies, Orders, Suppliers, Sorts, UserProfile, Emails, PhonenumbersComp, PhonenumbersSupp, \
    Messages, Tasks
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms.models import inlineformset_factory
from .forms import NewMessageForm
from .forms import UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import models


class SortAmountPriceCompany:
    """
    По началу брал всю информацию с заказов отдельно. Позже переработал метод.
    """
    def get_company(self):
        """
        :return: все объекты модели компаний для выпадающего списка на странице.
        Позже так и не понадобилось. Поиск организован вводом с клавиатуры в форме, а не выпадающим списком.
        """
        return Companies.objects.all()

    def get_done(self):
        """
        :return: статусы вполнения для заказа. Используется в выпадающем списке на странице списка заказов для фильтрации.
        """
        return Orders.DONE


class MarkUserManager:
    """
    Все менеджеры, оценки, каналы обращения для выпадаюего списка(функции комментировать не буду,
    работают аналогично предыдущему классу.
    """
    def get_manager(self):
        group = models.Group.objects.get(name='Manager')
        users = group.user_set.all()
        return users

    def get_mark(self):
        # marks = Messages.objects.values('mark')
        return Messages.MARK

    def get_channel(self):
        return Messages.CHANNEL


# проверка залогиненного пользователя, для возможности редактирования профиля.
# В принципе пользователь может редактировать только свой профиль.
@login_required
def edit(request):
    """
    После того, как пользователь редактирует данные на странице пользователя, они сохраняются в базе.
    """
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.userprofile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('profile', args=[str(request.user.userprofile.id)]))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.userprofile)
        return render(request,
                      'orders/edit.html',
                      {'user_form': user_form,
                       'profile_form': profile_form})

# формсеты, для того, чтобы при редактировании или создании новой компании\заказа\поставщика выводились дополнительные
# поля номеров телефона, емейлы и т.д.
PhoneCompFormset = inlineformset_factory(
    Companies, PhonenumbersComp, fields=('number',)
)
EmailsFormset = inlineformset_factory(
    Companies, Emails, fields=('email',)
)

PhoneSuppFormset = inlineformset_factory(
    Suppliers, PhonenumbersSupp, fields=('number',)
)


def home(request):
    """
    Домашная страница. Сделано анологично к библиотеке.
    :param request:
    :return: Возвращает рендер страницы с такими данными : количество компаний,
    количество заказов со статусом выполнено(filter(done='d'), количетсво поставщиков
    В добавок выводится, сколько раз посетил страницу пользователь(взято из библиотеки).
    Последний пункт не несет какой-либо смысловой нагрузки
    """
    num_companies = Companies.objects.all().count()
    num_orders = Orders.objects.filter(done="d").count()
    num_suppliers = Suppliers.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'home.html',
        context={'num_companies': num_companies, 'num_orders': num_orders,
                 'num_suppliers': num_suppliers, 'num_visits': num_visits},
    )


class CompaniesListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
    Список компаний. Стандартный метод. Добавлен пермишин для того, чтобы неавторизированный пользователь не смог
    вбить в строке ввода адреса страницу и перейти на нее. также обычный рядовой сотрудник
    не может посетить эту страницу(только менеджер)
    """
    model = Companies
    paginate_by = 5
    permission_required = 'orders.can_view_list_of_companies'

    def get_ordering(self):
        """
        :return: Вывод в алфавитном порядке по дефолту, но на странице реализована передача другого порядка вывода.
        """
        ordering = self.request.GET.get('order', 'name')
        return ordering


class CompanyDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """
    Стандартный класс для отображения детальной информации о компании. Пермишины для отображения информации только
    менеджеру.
    """
    model = Companies
    permission_required = 'orders.can_view_list_of_companies'

# следующие классы аналогично к предыдущим. Комментировать не вижу смысла
class SuppliersListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = Suppliers
    paginate_by = 5
    permission_required = 'orders.can_view_list_of_suppliers'


class SuppliersDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Suppliers
    permission_required = 'orders.can_view_list_of_suppliers'


class OrdersListView(LoginRequiredMixin, PermissionRequiredMixin, SortAmountPriceCompany, generic.ListView):
    model = Orders
    paginate_by = 5
    permission_required = 'orders.can_view_list_of_orders'


class OrdersDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Orders
    permission_required = 'orders.can_view_list_of_orders'


class MessagesListView(LoginRequiredMixin, PermissionRequiredMixin, MarkUserManager, generic.ListView):
    model = Messages
    paginate_by = 5
    permission_required = 'orders.can_view_list_of_messages'

    def get_queryset(self):
        return Messages.objects.order_by('-pub_date')


class MessagesDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Messages
    permission_required = 'orders.can_view_list_of_messages'


class AllMessagesByUserListView(LoginRequiredMixin, PermissionRequiredMixin, MarkUserManager, generic.ListView):
    """
    Класс для отображения сообщений авторизированного пользователя
    Указали другой шаблон
    """
    model = Messages
    template_name = 'orders/messages_list_by_user.html'
    paginate_by = 10
    permission_required = 'orders.can_view_list_of_messages'

    def get_queryset(self):
        """
        филтрация по пользователю, который дал запрос, вывод - сначала новые
        """
        return Messages.objects.filter(manager=self.request.user).order_by('-pub_date')


class TasksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = Tasks
    paginate_by = 5
    permission_required = 'orders.can_set_as_done'

    def get_queryset(self):
        return Tasks.objects.order_by('-done', '-pub_date')


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Tasks
    permission_required = (('orders.can_set_as_done'), ('orders.can_view_my_tasks'))


class MyTaskListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
    также как и с сообщениями
    """
    model = Tasks
    template_name = 'orders/mytask_list.html'
    paginate_by = 10
    permission_required = (('orders.can_set_as_done'), ('orders.can_view_my_tasks'))

    def get_queryset(self):
        return Tasks.objects.filter(excutors=self.request.user).order_by('-pub_date')


class CompanyCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    стандартный класс для создания новой компании. Включает в себя формсет для того, чтобы добавлять новые телефоны
    и емейлы
    """
    model = Companies
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_companies'

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["phonenumbers"] = PhoneCompFormset(self.request.POST)
            data['emails'] = EmailsFormset(self.request.POST)
        else:
            data["phonenumbers"] = PhoneCompFormset()
            data['emails'] = EmailsFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        phonenumbers = context["phonenumbers"]
        emails = context['emails']
        self.object = form.save()
        if phonenumbers.is_valid() and emails.is_valid():
            phonenumbers.instance = self.object
            emails.instance = self.object
            emails.save()
            phonenumbers.save()
        return super().form_valid(form)

    def get_success_url(self):
        """
        В случае если данные прошли переводит на страницу со списком всех компании
        :return:
        """
        return reverse_lazy("companies")


class CompanyUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Стандартный класс для редактирвования информации про компанию
    В поля заносится изначальная информация
    """
    model = Companies
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_companies'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["phonenumbers"] = PhoneCompFormset(self.request.POST, instance=self.object)
            data['emails'] = EmailsFormset(self.request.POST, instance=self.object)
        else:
            data["phonenumbers"] = PhoneCompFormset(instance=self.object)
            data['emails'] = EmailsFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        phonenumbers = context["phonenumbers"]
        emails = context['emails']
        self.object = form.save()
        if phonenumbers.is_valid() and emails.is_valid():
            emails.instance = self.object
            phonenumbers.instance = self.object
            emails.save()
            phonenumbers.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("companies")


class CompanyDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Удаление компании
    """
    model = Companies
    success_url = reverse_lazy('companies')
    permission_required = 'orders.can_view_list_of_companies'

# Следующие классы анолигичны классу созданию, редактирования и удаления компаний
class TaskCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Tasks
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_companies'


class TaskUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Tasks
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_companies'


class TaskDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Tasks
    success_url = reverse_lazy('tasks')
    permission_required = 'orders.can_view_list_of_companies'


class OrderCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Orders
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_orders'


class OrderUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Orders
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_orders'


class OrderDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Orders
    success_url = reverse_lazy('order')
    permission_required = 'orders.can_view_list_of_orders'


class SetTaskAsDone(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Класс для изменения статуса выполнения задания
    """
    model = Tasks
    fields = ['done', ]
    permission_required = (('orders.can_set_as_done'), ('orders.can_view_my_tasks'))


class SetOrderAsDone(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Класс для изменения статуса выполнения заказа
    """
    model = Orders
    fields = ['done', ]
    permission_required = (('orders.can_set_as_done'), ('orders.can_view_my_tasks'))


class MessageCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Messages
    form_class = NewMessageForm
    permission_required = 'orders.can_view_list_of_orders'

    def form_valid(self, form):
        form.instance.manager = self.request.user
        form.save()
        return redirect('/orders/messages')


class MessageUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Messages
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_orders'


class MessageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Messages
    success_url = reverse_lazy('messages')
    permission_required = 'orders.can_view_list_of_orders'


class SupplierCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Suppliers
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_orders'

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["phonenumbers"] = PhoneSuppFormset(self.request.POST)
        else:
            data["phonenumbers"] = PhoneSuppFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        phonenumbers = context["phonenumbers"]
        emails = context['emails']
        self.object = form.save()
        if phonenumbers.is_valid() and emails.is_valid():
            phonenumbers.instance = self.object
            emails.instance = self.object
            emails.save()
            phonenumbers.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("suppliers")


class SupplierUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Suppliers
    fields = '__all__'
    permission_required = 'orders.can_view_list_of_orders'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["phonenumbers"] = PhoneSuppFormset(self.request.POST, instance=self.object)
        else:
            data["phonenumbers"] = PhoneSuppFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        phonenumbers = context["phonenumbers"]
        self.object = form.save()
        if phonenumbers.is_valid():
            phonenumbers.instance = self.object
            phonenumbers.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("suppliers")


class SupplierDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Suppliers
    success_url = reverse_lazy('messages')
    permission_required = 'orders.can_view_list_of_orders'


class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    """
    Стандартный класс для просмотра детальной информации профиля пользователя
    """
    model = UserProfile


class FilterOrdersListView(SortAmountPriceCompany, generic.ListView):
    """
    Класс для отображения фильтрации по заказам. В шаблоне есть возможность указать параметры для фильтрации, которые
    передаются в этот класс и страница рендерится с новыми данными.
    """
    def get_queryset(self):
        queryset = Orders.objects.filter(
            Q(sort__in=self.request.GET.getlist('sort')) | Q(company__in=self.request.GET.getlist('company')) | Q(
                amount__in=self.request.GET.getlist('amount')) | Q(price__in=self.request.GET.getlist('price')) | Q(
                done__in=self.request.GET.getlist('done')))
        return queryset


class FilterMessagesListView(MarkUserManager, generic.ListView):
    """
    Аналогично предыдущему
    """
    def get_queryset(self):
        queryset = Messages.objects.filter(
            Q(manager__in=self.request.GET.getlist('manager')) | Q(mark__in=self.request.GET.getlist('mark')) | Q(
                channel__in=self.request.GET.getlist('channel')))
        return queryset

class Searchcomp(generic.ListView):
    """
    Класс для поиска компании. В шаблоне реализована возможность ввести название компании, передается в эту вьюшку
    и редерится страница с выводов компании по названию
    """
    def get_queryset(self):
        return Companies.objects.filter(name__icontains=self.request.GET.get('search'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search'] = self.request.GET.get('search')
        return context

class Searchtask(generic.ListView):
    """
    Аналоигчно компаниям, ищутся задания с названием переданным в поиске
    """
    def get_queryset(self):
        return Tasks.objects.filter(name__icontains=self.request.GET.get('search'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search'] = self.request.GET.get('search')
        return context

class Searchsupp(generic.ListView):
    """
    Поиск по фамилии поставщика.
    """
    def get_queryset(self):
        return Suppliers.objects.filter(last_name__icontains=self.request.GET.get('search'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search'] = self.request.GET.get('search')
        return context


