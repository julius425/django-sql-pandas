from django.urls import path
from . import views

urlpatterns = [
    # manage data base profiles
    path('', views.database_select, name='database_select'),
    path('database_update/<int:id>', views.database_update, name='database_update'),
    path('database_delete/<int:id>', views.database_delete, name='database_delete'),
    # node pages
    path('node_select/<int:id>', views.node_select, name='node_select'),
    path('node/<int:node_id>', views.node, name='node'),
    # node info pages
    path('frame_log/<int:node_id>', views.frame_log, name='frame_log'),
    path('frame_nunique/<int:node_id>', views.frame_nunique, name='frame_nunique'),
    path('frame_plot/<int:node_id>', views.frame_plot, name='frame_plot'),
    path('time_diff_plot/<int:node_id>', views.time_diff_plot, name='time_diff_plot'),
]

# auth
urlpatterns += [
    path('accounts/signup/', views.signup_view, name='signup')
]