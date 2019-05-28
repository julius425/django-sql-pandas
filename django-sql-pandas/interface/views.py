from django.shortcuts import render, redirect, get_object_or_404
from .forms import NodeModelForm, DataBaseModelForm, SignUpForm
from .models import NodeModel, DataBaseModel, Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import logging

# write logs in debug.log in BASE_DIR
logger = logging.getLogger(__name__)
logger.info("blah")


def signup_view(request):
    """Register account. Gets data from signup form"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def database_select(request):
    """Shows or creates database models."""
    template = 'db_select.html'
    profiles = Profile.objects.get(user=request.user)
    databases = DataBaseModel.objects.filter(profile=profiles)

    if request.method == 'POST':
        form = DataBaseModelForm(request.POST)
        if form.is_valid():
            dbase, created = DataBaseModel.objects.get_or_create(
                profile=Profile.objects.get(user=request.user),
                db_name=form.cleaned_data['db_name'],
                db_address=form.cleaned_data['db_address'],
                db_user=form.cleaned_data['db_user'],
                db_psswd=form.cleaned_data['db_psswd'],
                sql_name=form.cleaned_data['sql_name']
            )
            return redirect('database_select')
    else:
        form = DataBaseModelForm()

    context = {
        'form': form,
        'databases': databases,

    }

    return render(request, template, context)


@login_required
def database_update(request, id):
    """Updates database model."""
    db = DataBaseModel.objects.get(id=id)
    if request.method == 'POST':
        form = DataBaseModelForm(request.POST, instance=db)
        form.save()
        return redirect('database_select')
    else:
        form = DataBaseModelForm(initial={
            'db_name': db.db_name,
            'db_address': db.db_address,
            'db_user': db.db_user,
            'sql_name': db.sql_name
        })

    context = {
        'form': form
    }

    return render(request, 'db_update.html', context)


@login_required
def database_delete(request, id):
    """Deletes database profile model."""
    db = DataBaseModel.objects.get(id=id)
    if request.user == db.profile.user:
        db.delete()
    return redirect('database_select')


@login_required
def node_select(request, id):
    """
    Render a form that redirects to a specific node page if valid.

    """
    template = 'node_select.html'
    database = DataBaseModel.objects.get(id=id)

    if request.method == 'POST':
        form = NodeModelForm(request.POST)
        if form.is_valid():
            # Creates node model or updates it if model exists.
            node, created = NodeModel.objects.update_or_create(
                # data_base=DataBaseModel.objects.get(id=id),  # move to defaults?
                node_id=form.cleaned_data['node_id'],
                # Parameters to update if model exists
                defaults={
                    'data_base': database,
                    'time_from': form.cleaned_data['time_from'],
                    'time_to': form.cleaned_data['time_to']
                }
            )
            node.save()
            return redirect('node', node.node_id)
    else:
        form = NodeModelForm()

    context = {
        'form': form,
        'database': database
    }

    return render(request, template, context)


@login_required
def node(request, node_id):
    """Accepts node id, returns node page render"""
    node = get_object_or_404(NodeModel, node_id=node_id)
    template = "node.html"
    context = {
        'node': node
    }
    return render(request, template, context)


@login_required
def frame_nunique(request, node_id):
    """Accepts node id, returns nonunique messages page render for that id."""
    template = 'frame_nunique.html'
    node = get_object_or_404(NodeModel, node_id=node_id)
    data = node.frame_nunique()
    return render(request, template, {'data': data})


@login_required
def frame_log(request, node_id):
    """Accepts node id, returns node log page render for that id."""
    template = 'frame_log.html'
    node = get_object_or_404(NodeModel, node_id=node_id)
    data = node.frame_log()
    return render(request, template, {'data': data})


@login_required
def frame_plot(request, node_id):
    """Accepts node id, returns worktime plot page render for that id."""
    template = 'frame_plot.html'
    node = get_object_or_404(NodeModel, node_id=node_id)
    graphic = node.frame_plot()
    context = {
        'graphic': graphic,
    }
    return render(request, template, context)


@login_required
def time_diff_plot(request, node_id):
    """Accepts node id, returns worktime plot page render for that id."""
    template = 'frame_plot.html'
    node = get_object_or_404(NodeModel, node_id=node_id)
    graphic, sims = node.time_diff_plot()
    context = {
        'graphic': graphic,
        'node': node,
        'sims':sims
    }
    return render(request, template, context)



