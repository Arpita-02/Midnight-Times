import os
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from dj_rest_auth.views import LoginView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
import smtplib
from rest_framework.response import Response
from .models import User
from allauth.account.models import EmailAddress
from .permission import IsSuperUser
from advarisk.users.api.serializers import CustomTokenSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from dj_rest_auth.registration.views import RegisterView
from advarisk.users.api.serializers import CustomRegisterSerializer
from django.shortcuts import render

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    View to display user details.

    Attributes:
        model (Model): The model associated with this view.
        slug_field (str): The field used to retrieve the user.
        slug_url_kwarg (str): The URL keyword argument used to retrieve the user.
    """
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


def my_page_view(request):
    
    return render(request, 'account/admin_page.html')

# "admin_page.html"  # Specify the template to be used


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View to update user details.

    Attributes:
        model (Model): The model associated with this view.
        fields (list): List of fields to be updated.
        success_message (str): Message displayed upon successful update.
    """
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        """
        Get the URL to redirect to after a successful update.

        Returns:
            str: The URL to redirect to.
        """
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        """
        Get the object to be updated.

        Returns:
            User: The user object.
        """
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    View to redirect the user to their detail page.

    Attributes:
        permanent (bool): Whether the redirect is permanent.
    """
    permanent = False

    def get_redirect_url(self):
        """
        Get the URL to redirect to.

        Returns:
            str: The URL to redirect to.
        """
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class CustomLoginView(LoginView):
    """
    Custom login view to use a custom token serializer.

    Methods:
        get_response_serializer: Returns the custom token serializer.
    """

    def get_response_serializer(self):
        """
        Get the custom token serializer.

        Returns:
            CustomTokenSerializer: The custom token serializer.
        """
        return CustomTokenSerializer


class Invitation(viewsets.ModelViewSet):
    """
    Viewset to handle user invitations and blocking.

    Attributes:
        permission_classes (list): List of permission classes required for this viewset.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]

    def adduser(self, request):
        """
        Add a user by sending an invitation email or updating the verified status if the email already exists.

        Parameters:
            request (Request): The request object containing user data.

        Returns:
            Response: A response object with the success message or an error message.
        """
        recipient = request.data.get("email")
        if not recipient:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        email_addresses = EmailAddress.objects.filter(email=recipient)
        print(email_addresses)
        if email_addresses.exists():
            for email_address in email_addresses:
                print(email_address.verified, "------------------")
                email_address.verified = True
                email_address.save()
            return Response({"success": f"Successfully added {recipient}"}, status=status.HTTP_200_OK)
        else:
            subject = 'Invitation to Join'
            message = (
                'Dear recipient, you have been invited to register on our platform.\n\n'
                'Click here to register: http://0.0.0.0:8000/'
            )
            email_message = f'Subject: {subject}\n\n{message}'
            sender_email = os.getenv('sender_email')
            smtp_server = os.getenv('smtp_server')
            smtp_port = os.getenv('smtp_port')
            smtp_username = os.getenv('smtp_username')
            smtp_password = os.getenv('smtp_password')

            if not all([sender_email, smtp_server, smtp_port, smtp_username, smtp_password]):
                return Response({"error": "Email server configuration is incomplete"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                smtp_port = int(smtp_port)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender_email, recipient, email_message)
                return Response({"success": "Invitation sent successfully"}, status=status.HTTP_200_OK)
            except smtplib.SMTPException as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def blockuser(self, request):
        """
        Block a user by updating their verified status to False.

        Parameters:
            request (Request): The request object containing user data.

        Returns:
            Response: A response object with the success message or an error message.
        """
        recipient = request.data.get("email")
        email_addresses = EmailAddress.objects.filter(email=recipient)
        print(email_addresses)
        if email_addresses.exists():
            for email_address in email_addresses:
                print(email_address.verified, "------------------")
                email_address.verified = False
                email_address.save()
            return Response({"success": f"Block user {recipient} successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": f"user {recipient} not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            import json
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Replace with actual token logic
                return JsonResponse({'access_token': 'fake-token-for-demo'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
