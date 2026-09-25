import truststore
truststore.inject_into_ssl()
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.cache import never_cache

from django.conf import settings
from hr.models import Employee, Department, Designation, Leave


# Create your views here.

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            if Employee.objects.filter(user=user).exists():
                print("enter----------1")
                return redirect("employee_dashboard")
            print("enter----------2")
            return redirect("dashboard")
        return render(request,"login.html",{"error": "Invalid username or password"})
    return render(request, "login.html")



@login_required
@never_cache
def dashboard(request):
    return render(request,"dasboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")




@login_required
@never_cache
def viewemployees(request):
    employees=(Employee.objects.select_related("department","designation").filter(status=True))
    return render(request,"employeelist.html",{"employees":employees})

@login_required
@never_cache
def employee_create(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        # Check duplicate email
        if User.objects.filter(email=email).exists():
            return render(
                request,
                "employee_add_update.html",
                {
                    "departments": departments,
                    "designations": designations,
                    "employment_types": Employee.EMPLOYMENT_TYPES,
                    "is_update": False,
                    "email_error": "User email already exists."
                }
            )
        phone = request.POST.get("phone")

        department_id = request.POST.get("department")
        designation_id = request.POST.get("designation")

        joining_date = request.POST.get("joining_date")
        employment_type = request.POST.get("employment_type")
        salary = request.POST.get("salary")
        address = request.POST.get("address")

        status = request.POST.get("status") == "on"
        if Employee.objects.filter(email=email).exists():
            messages.error(
                request,
                "Employee with this email already exists."
            )
            return redirect("employee_create")

        # Create Django User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name
        )

        # Disable password until employee creates one
        user.set_unusable_password()
        user.save()

        # Create Employee
        employee = Employee.objects.create(
            user=user,
            employee_id=employee_id,
            name=name,
            email=email,
            phone=phone,
            department_id=department_id,
            designation_id=designation_id,
            joining_date=joining_date,
            employment_type=employment_type,
            salary=salary,
            address=address,
            status=status
        )

        # Generate password setup token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Password setup URL
        setup_link = request.build_absolute_uri(
            reverse(
                "set_password",
                kwargs={
                    "uidb64": uid,
                    "token": token
                }
            )
        )

        # Send email
        # Send email
        try:
            send_mail(
                subject="CrewConnect - Set Your Password",
                message=f"""
        Hello {name},

        Your CrewConnect employee account has been created.

        Please click the link below to create your password:

        {setup_link}

        After setting your password, you can log in to CrewConnect.

        Regards,
        CrewConnect HR
        """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Employee added successfully and email sent."
            )

        except Exception as e:
            print("EMAIL ERROR:", e)

            messages.warning(
                request,
                "Employee added successfully, but email could not be sent."
            )

        return redirect("employee_list")




    return render(
        request,
        "employee_add_update.html",
        {
            "departments": departments,
            "designations": designations,
            "employment_types": Employee.EMPLOYMENT_TYPES,
            "is_update": False,
        }
    )

@login_required
@never_cache
def employee_update(request, id):


    employee = get_object_or_404(Employee,id=id)


    departments = Department.objects.all()
    designations = Designation.objects.all()


    if request.method == "POST":


        employee.employee_id = request.POST.get("employee_id")
        employee.name = request.POST.get("name")
        employee.email = request.POST.get("email")
        employee.phone = request.POST.get("phone")


        employee.department_id = request.POST.get("department")
        employee.designation_id = request.POST.get("designation")


        employee.joining_date = request.POST.get("joining_date")
        employee.employment_type = request.POST.get("employment_type")
        employee.salary = request.POST.get("salary")
        employee.address = request.POST.get("address")


        employee.status = request.POST.get("status") == "on"


        employee.save()


        return redirect(
            "employee_list"
        )


    return render(
        request,
        "employee_add_update.html",
        {
            "employee": employee,
            "departments": departments,
            "designations": designations,
            "employment_types": Employee.EMPLOYMENT_TYPES,
            "is_update": True,
        }
    )


@login_required
@never_cache

def employee_delete(request, id):
    employee = get_object_or_404(
        Employee,
        id=id
    )
    employee.status = not employee.status
    employee.save()
    return redirect("employee_list")

@login_required
def leave_approve(request):


   # Check whether logged-in user is an employee
   if Employee.objects.filter(user=request.user).exists():
       return redirect("employee_dashboard")


   leaves = Leave.objects.select_related(
       "employee",
       "employee__department",
       "employee__designation"
   ).order_by("-applied_date")


   return render(
       request,
       "leave_approval.html",
       {
           "leaves": leaves,
           "is_employee": False,
       }
   )
@login_required
def leave_action(request, id):


    # Employee cannot approve/reject
    if Employee.objects.filter(user=request.user).exists():
        return redirect("employee_dashboard")


    if request.method == "POST":


        leave = Leave.objects.get(id=id)


        action = request.POST.get("action")


        if action == "approve":


            leave.status = "Approved"
            leave.save()


        elif action == "reject":


            leave.status = "Rejected"
            leave.save()


    return redirect("leave_approve")


@login_required
def departments(request):

    # Employee cannot access departments page
    if Employee.objects.filter(user=request.user).exists():
        return redirect("employee_dashboard")

    departments = Department.objects.all().order_by("name")

    return render(
        request,
        "departments.html",
        {
            "departments": departments,
        }
    )
@login_required
def designations(request):

    # Employee cannot access designations page
    if Employee.objects.filter(user=request.user).exists():
        return redirect("employee_dashboard")

    designations = Designation.objects.all().order_by("name")

    return render(
        request,
        "designations.html",
        {
            "designations": designations,
        }
    )