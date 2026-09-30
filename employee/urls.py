from django.urls import path

from employee import views

urlpatterns = [
    path("set-password/<uidb64>/<token>/",views.set_password,name="set_password"),
    path("dashboard/",views.employee_dashboard,name="employee_dashboard"),
    path("profile/",views.employee_profile,name="my_profile"),
    path("apply_leave/",views.apply_leave,name="apply_leave"),
    path("my_leaves/",views.my_leaves,name="my_leaves"),
path("leave_calender/",views.leave_calender,name="leave_calender"),
path("resend-password/<str:employee_id>/",views.resend_password_email,name="resend_password_email"),
path("my-payslips/",views.my_payslips,name="my_payslips"),
path("payroll/",views.payroll_list,name="payroll_list"),

path("payroll/create/",views.payroll_create,name="payroll_create"),
path("designations/", views.designations, name="designations"),
path("reports/", views.reports, name="reports"),
path("departments/",views.departments,name="departments"),
    ]