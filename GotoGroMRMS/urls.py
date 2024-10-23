from django.contrib import admin # Import admin module to enable Django admin interface
from django.urls import path # Import path function to define URL patterns
from django.contrib.auth import views as auth_views # Import authentication views for login and logout
from members import views as member_views # Import views from members app
from members.views import custom_logout # Import custom logout view from members app


# URL patterns for project
urlpatterns = [
        
        # URL pattern for Django admin interface
        path('admin/', admin.site.urls),

        # URL pattern for home page, mapped to home view in members app
        path('', member_views.home, name='home'), 

        # URL pattern for user registration page, mapped to register view in members app
        path('register/', member_views.register, name='register'),
        
        # URL pattern for user profile page, mapped to profile view in members app
        path('profile/', member_views.profile, name='profile'),

        path('profile/update/', member_views.update_profile, name='update_profile'),
        
        path('profile/change-password/', member_views.change_password, name='change_password'),
        
        # URL pattern for redirecting default account profile path to the custom profile view
        path('accounts/profile/', member_views.profile_redirect, name='profile_redirect'),

        # URL pattern for deleting user profile
        path('delete_profile/', member_views.delete_profile, name='delete_profile'),

        # URL pattern for viewing transaction history, mapped to transaction_history view
        path('transactions/', member_views.transaction_history, name='transaction_history'),

        # URL pattern for adding new transactions, mapped to add_transaction view
        path('transactions/add/', member_views.add_transaction, name='add_transaction'),

        # URL pattern for deleting transactions, mapped to delete_transactions view
        path('transactions/delete/', member_views.delete_transactions, name='delete_transactions'),

        # URL pattern for accessing dashboard, mapped to dashboard view
        path('dashboard/', member_views.dashboard, name='dashboard'),

        path('record-sale/', member_views.record_sale, name='record_sale'),

        path('sales-history/', member_views.sales_history, name='sales_history'),

        path('sales/update/<int:sale_id>/', member_views.update_sale, name='update_sale'),
        
        path('delete-sales/', member_views.delete_sales, name='delete_sales'),

        #  URL patterns for user login with Django login view with custom login template
        path('login/', auth_views.LoginView.as_view(template_name='members/login.html'), name='login'),

        # URL pattern for user logout with Django logout view
        path('logout/', custom_logout, name='logout'),
]
        