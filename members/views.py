from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm, SaleUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Transaction, Profile, Sale
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model

def home(request):
    return render(request, 'members/home.html')

def profile_redirect(request):
    return redirect('profile')

# View to handle user registration
def register(request):
    if request.method == 'POST':

        # Show the registration form with POST data
        form = UserRegisterForm(request.POST)
        if form.is_valid():

            # Save the new user into the database
            user = form.save()

            # Retrieve user name from cleaned form data
            username = form.cleaned_data.get('username')

            # Notify user of account creation when successful
            messages.success(request, f'Account created for {username}.')

            # Log user in after successful registration
            login(request, user)

            # Redirect user to profile page
            return redirect('profile')
        
    else:
        # If request is not POST, show empty registration form
        form = UserRegisterForm()

    # Render registration template with form context    
    return render(request, 'members/register.html', {'form': form})

# View to handle display and update of user profile
# Ensures that only validated users can access this view
@login_required
def profile(request):

    if request.method == 'POST':
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Account profile has been updated.')
            return redirect('profile')

        else:
            print("User Update Form Errors:", u_form.errors)
            print("Profile Update Form Errors:", p_form.errors)

    else:

        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Context dictionary to pass the forms to the template
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    # Renders the profile template with form context
    return render(request, 'members/profile.html', context)

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'members/transactions.html', {'transactions': transactions})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        Transaction.objects.create(user=request.user, amount=amount, description=description)
        messages.success(request, 'Transaction added successfully.')
        return redirect('transaction_history')
    return render(request, 'members/add_transaction.html')

@login_required
def dashboard(request):
    return render(request, 'members/dashboard.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('home')

@login_required
def delete_transactions(request):
    if request.method == 'POST':
        transaction_ids = request.POST.getlist('transactions')
        if transaction_ids:
            Transaction.objects.filter(id__in=transaction_ids, user=request.user).delete()
            messages.success(request, 'Selected transactions have been deleted.')
        
        else:
            messages.warning(request, 'No transactions have been selected for deletion.')
        return redirect('transaction_history')
    

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        # Save user ID to delete after confirming
        user_id = user.id
        user.delete() # Deletes the user account
        messages.success(request, 'Your profile has been deleted successfully.')
        return redirect('home') #redirect to home
    

@login_required
def record_sale(request):
    if request.method == 'POST':
        member = request.user
        item_name = request.POST['item_name']
        purchase_quantity = int(request.POST['purchase_quantity'])
        total_price = float(request.POST['total_price'])

        sale = Sale.objects.create(
            member = member,
            item_name = item_name,
            purchase_quantity = purchase_quantity,
            total_price = total_price
        )

        return redirect('sales_history')
    
    return render(request, 'members/record_sale.html')


@login_required
def sales_history(request):
    sales = Sale.objects.filter(member=request.user).order_by('-purchase_date')
    return render(request, 'members/sales_history.html', {'sales': sales})


@login_required
def update_sale(request, sale_id):
    sale= get_object_or_404(Sale, id=sale_id)

    if request.method == 'POST':
        form = SaleUpdateForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sales_history')    
    
    else:
        form = SaleUpdateForm(instance=sale)

    return render(request, 'members/update_sale.html', {'form':form})     

@login_required
def delete_sales(request):
    if request.method == 'POST':
        sale_ids = request.POST.getlist('sales')
        Sale.objects.filter(id__in=sale_ids).delete()
    return redirect('sales_history')

@login_required
def update_profile(request):
    if request.method == 'POST':
         u_form = UserUpdateForm(request.POST, instance=request.user)
         p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

         if u_form.is_valid() and p_form.is_valid():
            #Save user model
            u_form.save()
            
            #Save profile model
            profile = p_form.save(commit=False)

            #Update first name and last name in Profile for user model
            profile.first_name = request.user.first_name
            profile.last_name = request.user.last_name

            # Save updated profile
            profile.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to profile view
         
         else:
             print("User Update Form Errors:", u_form.errors)  # Debugging line
             print("Profile Update Form Errors:", p_form.errors)  # Debugging line
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'members/update_profile.html', context)

@login_required
def change_password(request):
    
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)
      
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('profile')
            
    else:
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'members/change_password.html', {'password_form': password_form})