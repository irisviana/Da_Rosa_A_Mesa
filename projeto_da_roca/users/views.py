import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate,logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import ServiceAddress
from .models import User
from .models import DeliveryTime
from .forms import UserForm

# Create your views here.


def list_users(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def create_users(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserForm()
    return render(request, '../templates/registration/create_costumer.html', {'form': form})


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'email ou senha estão incorretos')

    return render(request, 'registration/login.html')


def logout_page(request):
    logout(request)
    return render(request, 'registration/login.html')


def home(request):
    return render(request, 'home.html')


class ServiceAddressView:
    @classmethod
    def list_service_address(cls, request):
        service_address = ServiceAddress.objects.all()

        return render(request, '../templates/service_address/home.html', {
            "services_address": service_address,
        })


    @classmethod
    def create_service_address(cls, request):
        message = ''
        if request.method == 'POST':
            city = request.POST['cidade']
            state = request.POST['estado']
            userId = request.POST['usuarioId']

            user = User.objects.get(id = userId)
            
            service_address = ServiceAddress(
                userId=user, city=city, state=state)

            service_address.save()

            message = "Endereço de atendimento criado com sucesso."

        return render(request, '../templates/service_address/create.html', {
            'message': message,
        })

    @classmethod
    def update_service_address(cls, request):
        message = ''
        if request.method == 'POST':
            service_address_id = request.POST['enderecoEntredaId']
            city = request.get('cidade')
            state = request.get('estado')
            
            service_address = ServiceAddress.objects.get(id=service_address_id)
            
            service_address.update(
                city=city if city else service_address.city,
                state=state if state else service_address.state)

            message = "Endereço de atendimento atualizado com sucesso."

        return render(request, 'usuario/service_address/create.html', {
            'mesage': message,
        })

    @classmethod
    def delete_service_address(cls, request):
        message = ''
        if request.method == 'POST':
            service_address_id = request.POST['enderecoAtendimentoId']
            
            try:
                service_address = ServiceAddress.objects.get(id=service_address_id)
                service_address.delete()

                message = "Endereço de atendimento deletado com sucesso."
            except ServiceAddress.DoesNotExist as e:
                print(str(e)) 
                message = 'Endereço de entrega não existe.'

            services_address = ServiceAddress.objects.all()
            
        return render(request, '../templates/service_address/home.html', {
            "message": message,
            'service_address': services_address,
        })

class DeliveryTimeView:
    @classmethod
    def list_delivery_time(cls, request):
        delivery_time = DeliveryTime.objects.all()

        return render(request, '../templates/delivery_time/home.html', {
            "delivery_times": delivery_time,
        })

    @classmethod
    def create_delivery_time(cls, request):
        message = ''
        if request.method == 'POST':
            service_address_id = request.POST['enderecoAtendimentoId']
            time = request.POST['hora']
            day = request.POST['dia']

            service_address = ServiceAddress.objects.get(id=service_address_id)

            delivery_time = DeliveryTime(
                service_address=service_address, time=time, dia=day)

            delivery_time.save()

            message = 'Horário de entrega criado com sucesso.'
        
        return render(request, '../templates/delivery_time/create.html', {
            'message': message,
        })

    @classmethod
    def update_delivery_time(cls, request):
        message = ''
        if request.mothod == 'POST':
            delivery_time_id = request.POST['horarioEntregaId']
            time = request.POST.get('time', None)
            day = request.POST.get('day', None)

            delivery_time = DeliveryTime.objects.get(id=delivery_time_id)

            delivery_time.update(
                time=time if time else delivery_time.time,
                day=day if day else delivery_time.day)

            message = 'Horário de entrega atualizado com sucesso.'

        return render(request, 'usuario/delivery_time/create.html', {
            'mensagem': message,
        })

    @classmethod
    def delete_delivery_time(cls, request):
        message = ''
        if request.method == 'POST':
            delivery_time_id = request.POST['horarioEntregaId']

            try:
                delivery_time = DeliveryTime.objects.get(id=delivery_time_id)
                delivery_time.delete()

                message = 'Horário de entrega removido com sucesso.'
            except DeliveryTime.DoesNotExist as e:
                print(str(e))
                message = 'Horário de entrega não existe.'

            delivery_times = DeliveryTime.objects.all()

        return render(request, '../templates/delivery_time/home.html', {
            'message': message,
            'delivery_time': delivery_times,
        })
