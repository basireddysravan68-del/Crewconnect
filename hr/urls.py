from django.urls import path

from hr import views

urlpatterns = [
    path("",views.login_view,name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("viewemployees/", views.viewemployees, name="employee_list"),

    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:id>/edit/",views. employee_update, name="employee_update"),
    path("employees/<int:id>/delete/",views. employee_delete, name="employee_delete"),
    path('leave_approve/',views.leave_approve,name="leave_approve"),
    path('leave/<int:id>/action/',views.leave_action,name="leave_action"),
    path('departments/',views.departments,name="departments"),
    path('designations/',views.designations,name="designations"),

    ]