from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.messages import add_message, constants
from django.shortcuts import redirect, render, resolve_url

from medico.models import is_medico


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')

        users = User.objects.filter(username=username)

        if users.exists():
            add_message(
                request,
                constants.ERROR,
                "Já existe um usuário com esse username"
            )
            return redirect('/usuarios/cadastro')

        if senha != confirmar_senha:
            add_message(
                request,
                constants.ERROR,
                "A senha e o confirmar senha devem ser iguais"
            )
            return redirect('/usuarios/cadastro')

        if len(senha) < 6:
            add_message(
                request,
                constants.ERROR,
                "A senha deve ter mais de 6 dígitos"
            )
            return redirect('/usuarios/cadastro')

        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=senha
            )
            return redirect('/usuarios/login')
        except Exception:
            print('Erro 4')
            return redirect('/usuarios/cadastro')


def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get("senha")

        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            url = "consultas_medico" if is_medico(user) else "minhas_consultas"
            return redirect(resolve_url(url))

        add_message(
            request,
            constants.ERROR,
            'Usuário ou senha incorretos'
        )

        return redirect(resolve_url("login"))


def sair(request):
    auth.logout(request)
    return redirect('/usuarios/login')
