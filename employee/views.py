from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from datetime import datetime
from Crewconnect import settings
from hr.models import Leave, Employee, Department
from hr.models import Employee, Payroll, Payslip, Designation


# Create your views here.
def set_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "invalid_link.html")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(
                "set_password",
                uidb64=uidb64,
                token=token
            )

        user.set_password(password)
        user.save()

        messages.success(
            request,
            "Password created successfully. You can now login."
        )

        return redirect("login")

    return render(request, "set_password.html")



@login_required
def employee_dashboard(request):


   employee = request.user.employee


   return render(request,"employee_dashboard.html",{
           "employee": employee,"is_employee": True,})

@login_required
def employee_profile(request):
    employee = request.user.employee

    return render(request, "profile.html", {
        "user": employee, "is_employee": True, })

@login_required
def apply_leave(request):

    employee = Employee.objects.get(user=request.user)

    if request.method == "POST":

        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        try:
            start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter a valid date."
            )

            return redirect("apply_leave")

        if end_date < start_date:

            messages.error(
                request,
                "End date cannot be before start date."
            )

            return redirect("apply_leave")

        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending"
        )

        messages.success(
            request,
            "Leave applied successfully."
        )

        return redirect("my_leaves")

    return render(request, "apply_leave.html")

@login_required
def my_leaves(request):

    employee = request.user.employee

    leaves = Leave.objects.filter(
        employee=employee
    ).order_by("-applied_date")

    return render(
        request,
        "my_leaves.html",
        {
            "leaves": leaves,
            "is_employee": True,
        }
    )
@login_required
def leave_calender(request):

    employee = request.user.employee

    leaves = Leave.objects.filter(
        employee=employee
    ).order_by("start_date")

    return render(
        request,
        "leave_calendar.html",
        {
            "leaves": leaves,
            "is_employee": True,
        }
    )


def resend_password_email(request, employee_id):
    employee = Employee.objects.get(employee_id=employee_id)
    user = employee.user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    setup_link = request.build_absolute_uri(
        reverse(
            "set_password",
            kwargs={
                "uidb64": uid,
                "token": token
            }
        )
    )

    send_mail(
        subject="CrewConnect - Set Your Password",
        message=f"""
Hello {employee.name},

Your CrewConnect employee account has been created.

Please click the link below to create your password:

{setup_link}

After setting your password, you can log in to CrewConnect.

Regards,
CrewConnect HR
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[employee.email],
        fail_silently=False,
    )

    messages.success(
        request,
        "Password setup email sent successfully."
    )

    return redirect("employee_list")


@login_required
def my_payslips(request):
    employees = Employee.objects.select_related(
        "department",
        "designation"
    ).all().order_by("employee_id")

    selected_employee = None
    payrolls = []

    employee_id = request.GET.get("employee")

    if employee_id:
        try:
            selected_employee = Employee.objects.select_related(
                "department",
                "designation"
            ).get(id=employee_id)

            payrolls = Payroll.objects.filter(
                employee=selected_employee
            ).order_by("-month")

        except Employee.DoesNotExist:
            selected_employee = None

    return render(
        request,
        "my_payslips.html",
        {
            "employees": employees,
            "selected_employee": selected_employee,
            "payrolls": payrolls,
        }
    )

@login_required
def payroll_list(request):

    payrolls = Payroll.objects.select_related(
        "employee"
    ).order_by("-created_at")

    return render(
        request,
        "payroll_list.html",
        {
            "payrolls": payrolls
        }
    )

@login_required
def payroll_create(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee")
        month = request.POST.get("month")
        basic_salary = request.POST.get("basic_salary")
        allowances = request.POST.get("allowances") or 0
        deductions = request.POST.get("deductions") or 0

        employee = Employee.objects.get(id=employee_id)

        Payroll.objects.create(
            employee=employee,
            month=month,
            basic_salary=basic_salary,
            allowances=allowances,
            deductions=deductions
        )

        messages.success(
            request,
            "Payroll created successfully."
        )

        return redirect("payroll_list")

    return render(
        request,
        "payroll_create.html",
        {
            "employees": employees
        }
    )

@login_required
def departments(request):
    departments = Department.objects.all().order_by("name")

    return render(
        request,
        "departments.html",
        {
            "departments": departments
        }
    )
@login_required
def designations(request):
    designations = Designation.objects.all().order_by("name")

    return render(
        request,
        "designations.html",
        {"designations": designations}
    )

@login_required
def reports(request):
    employees_count = Employee.objects.count()
    payroll_count = Payroll.objects.count()
    payslip_count = Payslip.objects.count()

    return render(
        request,
        "reports.html",
        {
            "employees_count": employees_count,
            "payroll_count": payroll_count,
            "payslip_count": payslip_count,
        }
    )