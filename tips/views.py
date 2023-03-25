from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django import forms
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required

from .models import Cafe, Waiter, User, Customer
from .forms import NewUserForm


class IndexView(generic.ListView):
    template_name = "tips/index.html"
    context_object_name = "cafes_list"

    def get_queryset(self):
        return Cafe.objects.order_by("-title")[:10]


class CafeView(generic.DetailView):
    model = Cafe
    template_name = "tips/cafe.html"

    def get_object(self):
        return self.model.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(CafeView, self).get_context_data()
        context["waiters_list"] = self.object.waiter_set.all()
        context["cafe_admins_list"] = self.object.cafeadmin_set.all()
        return context


class WaiterView(generic.DetailView):
    model = Waiter
    template_name = "tips/waiter.html"

    def get_object(self):
        return self.model.objects.get(cafe=Cafe.objects.get(slug=self.kwargs['cafe_slug']), user=User.objects.get(username=self.kwargs['waiter_username']))


@login_required
def iamview(request, username):
    user_form_class = modelform_factory(User, fields=['first_name', 'last_name', 'email'], widgets={'first_name': forms.TextInput, 'last_name': forms.TextInput, 'email': forms.EmailInput})
    customer_form_class = modelform_factory(Customer, fields=["customer_wallet"], widgets={"customer_wallet": forms.TextInput})
    waiter_form_class = modelform_factory(Waiter, fields=["waiter_wallet"], widgets={"waiter_wallet": forms.TextInput})
    if request.method == "POST":
        user_form = user_form_class(request.POST, instance=request.user)
        customer_form = customer_form_class(request.POST, instance=request.user.customer)
        waiter_forms = {waiter.cafe.slug: waiter_form_class(request.POST, instance=waiter) for waiter in request.user.waiter_set.all()}
        if user_form.is_valid():
            user_form.save()
            if len(user_form.changed_data) > 0:
                messages.success(request, "Your user profile was updated successfully")
            return redirect('tips:user', username=request.user.username)
        if customer_form.is_valid():
            customer_form.save()
            if len(customer_form.changed_data) > 0:
                messages.success(request, "Customer wallet was changed successfully.")
            return redirect('tips:user', username=request.user.username)
        for cafe in waiter_forms:
            if waiter_forms[cafe].is_valid():
                waiter_forms[cafe].save()
                if len(waiter_forms[cafe].changed_data) > 0:
                    messages.success(request, f"Waiter wallet for cafe {cafe} was changed successfully.")
                return redirect('tips:user', username=request.user.username)
    else:
        user_form = user_form_class(instance=request.user)
        customer_form = customer_form_class(instance=request.user.customer)
        waiter_forms = {waiter.cafe.slug: waiter_form_class(instance=waiter) for waiter in request.user.waiter_set.all()}
    context = {
        "user": request.user,
        "waiters_list": request.user.waiter_set.all(),
        "cafe_admins_list": request.user.cafeadmin_set.all(),
        "user_form": user_form,
        "customer_form": customer_form,
        "waiter_forms": waiter_forms
    }
    return render(request=request, template_name="tips/iam.html", context=context)


def registration(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("tips:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="tips/register.html", context={"register_form":form})


def login_user(request):  # custom auth form? OTP?
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.info(request, f"You are now logged in as {username}.")
            return redirect("tips:index")
        messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="tips/login.html", context={"login_form":form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("tips:index")
