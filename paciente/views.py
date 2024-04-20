from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.messages import add_message, constants
from django.shortcuts import redirect, render, resolve_url

from medico.models import DadosMedico, DatasAbertas, Especialidades, is_medico

from .models import Consulta


@login_required
def home(request):
    if request.method == "GET":
        if is_medico:
            add_message(
                request,
                constants.WARNING,
                "Área apenas para pacientes."
            )

            return redirect(resolve_url("consultas_medico"))

        medicos = DadosMedico.objects.all()
        especialidades = Especialidades.objects.all()
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(
                especialidade_id__in=especialidades_filtrar)

        return render(
            request,
            'home.html',
            {
                "medicos": medicos,
                "especialidades": especialidades,
                "is_medico": is_medico(request.user),
            }
        )


@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(
            user=medico.user
        ).filter(
            data__gte=datetime.now()
        ).filter(
            agendado=False
        )

        return render(
            request,
            "escolher_horario.html",
            {
                'medico': medico,
                'datas_abertas': datas_abertas,
                "is_medico": is_medico(request.user),
            }
        )


@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        # TODO: Sugestão Tornar atomico

        data_aberta.agendado = True
        data_aberta.save()

        add_message(request, constants.SUCCESS,
                    'Horário agendado com sucesso.')

        # return redirect('/pacientes/minhas_consultas/')
        return redirect(resolve_url("minhas_consultas"))


@login_required
def minhas_consultas(request):
    print("vim pra cá")
    if request.method == "GET":
        if is_medico:
            add_message(
                request,
                constants.WARNING,
                "Área apenas para pacientes."
            )

            return redirect(resolve_url("consultas_medico"))

        # TODO: desenvolver filtros
        minhas_consultas = Consulta.objects.filter(
            paciente=request.user
        ).filter(
            data_aberta__data__gte=datetime.now()
        )
        return render(
            request,
            'minhas_consultas.html',
            {
                'minhas_consultas': minhas_consultas,
                "is_medico": is_medico(request.user),

            }
        )


@login_required
def consulta(request, id_consulta):
    if not is_medico(request.user):
        add_message(
            request,
            constants.WARNING,
            'Somente médicos podem acessar essa página.'
        )
        return redirect(resolve_url("sair"))

    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)

        return render(
            request,
            'consulta.html',
            {
                'consulta': consulta,
                'dado_medico': dado_medico,
                'is_medico': is_medico(request.user)
            }
        )
