from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm, SaleUpdateForm, InventoryUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Transaction, Profile, Sale, Inventory, Notification
from django.db.models import Sum, Avg
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import csv

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
        price_per_unit = float(request.POST['price_per_unit'])

        total_price = purchase_quantity * price_per_unit
        
        # Fetch the inventory amount for the item or assume the default if it doesn't exist
        try:
            inventory = Inventory.objects.get(item_name=item_name)
            inventory_amount = inventory.inventory_amount

        except Inventory.DoesNotExist:
            inventory_amount = 1000  # Default inventory amount

            # Create a new Inventory record with the default amount if it doesn't exist
            inventory = Inventory.objects.create(item_name=item_name, inventory_amount=inventory_amount)

        # Validate the purchase quantity against the inventory amount
        if purchase_quantity > inventory_amount:
            messages.error(request, f"Purchase quantity exceeds available inventory ({inventory_amount}) for {item_name}.")
            return redirect('record_sale')

        
        # Proceed to record the sale
        sale = Sale.objects.create(
            member = member,
            item_name = item_name,
            purchase_quantity = purchase_quantity,
            price_per_unit=price_per_unit,
            total_price = total_price
        )

        # Update inventory remaining quantity
        inventory.remaining_quantity -= purchase_quantity
        inventory.save()

        # Trigger notification based on conditions
        if 100 <= purchase_quantity <= 1000:
            Notification.objects.create(
                type='high_purchase_quantity',
                message = f"{member.username} recorded a high purchase quantity of {purchase_quantity} for {item_name}. Verification is required.",
                triggered_by = member
            )

        # Check total sales amount for this item by the user
        total_sales_amount = Sale.objects.filter(item_name=item_name, member=member).aggregate(total=Sum('total_price'))['total'] or 0
        if total_sales_amount > 100000:
            Notification.objects.create(
                type='high_sales_amount',
                message = f"{member.username} has exceeded a sales total of 100,000 for {item_name}. Verification is required.",
                triggered_by = member
            )

        # Low inventory notification
        if inventory.remaining_quantity <= 50:
            Notification.objects.create(
                type='low_inventory',
                message=f"Inventory for {item_name} is low: {inventory.remaining_quantity} remaining.",
                triggered_by = request.user
            )    

        return redirect('sales_history')
    
    return render(request, 'members/record_sale.html')


@login_required
def sales_history(request):

    if request.user.is_superuser:
    
        sales = Sale.objects.all() #Superuser can see all sales
    
    else:

        #Normal users can only see their sales
        sales = Sale.objects.filter(member=request.user).order_by('-purchase_date')
    
    return render(request, 'members/sales_history.html', {'sales': sales})


@login_required
def update_sale(request, sale_id):
    sale= get_object_or_404(Sale, id=sale_id)

    if request.method == 'POST':
        form = SaleUpdateForm(request.POST, instance=sale)
        if form.is_valid():
            new_purchase_quantity = form.cleaned_data['purchase_quantity']

            # Fetch inventory record for sale item
            try:
                inventory = Inventory.objects.get(item_name=sale.item_name)
                inventory_amount = inventory.inventory_amount

            except Inventory.DoesNotExist:
                #Default inventory amount if no record exists
                inventory_amount = 1000
                inventory = Inventory.objects.create(item_name=sale.item_name, inventory_amount=inventory_amount)

            # Calculate available quantity including current sale quantity
            available_quantity = inventory_amount + sale.purchase_quantity - new_purchase_quantity

            # Check if new purchase quantity exceeds available quantity
            if new_purchase_quantity > available_quantity:
                messages.error(request, f"Purchase quantity cannot exceed available inventory ({available_quantity}) for {sale.item_name}.")
                return redirect('update_sale', sale_id=sale_id)

            # Save updated sale and adjust inventory's remaining quantity   
            sale.purchase_quantity = new_purchase_quantity 
            sale.save()
            inventory.remaining_quantity = max(inventory.inventory_amount - new_purchase_quantity, 0)
            inventory.save()

            # Trigger notifications based on conditions
            if 100 <= new_purchase_quantity <= 1000:
                Notification.objects.create(
                    type='high_purchase_quantity',
                    message = f"{request.user.username} updated purchase quantity to a high value of {new_purchase_quantity} for {sale.item_name}.",
                    triggered_by = request.user
                )

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

    return render(request, 'members/change_password.html', {'password_form': password_form})\
    

@login_required
def inventory_list(request):
    inventories = Inventory.objects.all()
    
    for inventory in inventories:
        # Fetch total purchase quantity for item
        total_purchase_quantity = Sale.objects.filter(item_name=inventory.item_name).aggregate(
            total=Sum('purchase_quantity')
        )['total'] or 0 #default to 0 if no sales found


        # Fetch latest sale price for item
        latest_sale = Sale.objects.filter(item_name = inventory.item_name).order_by('-purchase_date').first()
        price_per_unit = latest_sale.price_per_unit if latest_sale else None

        # Add these attributes to each inventory item
        inventory.total_purchase_quantity = total_purchase_quantity
        inventory.price_per_unit = price_per_unit
        
        context = {
            'inventories' : inventories
        }

    return render(request, 'members/inventory.html', {'inventories': inventories})

@login_required
def update_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)

    if request.method == 'POST':
        form = InventoryUpdateForm(request.POST, instance=inventory)
        if form.is_valid():

            # Get the new inventory amount from form data
            new_inventory_amount = form.cleaned_data['inventory_amount']

            # Calculate total purchase quantity for this item
            total_purchase_quantity = Sale.objects.filter(item_name=inventory.item_name).aggregate(    
                total=Sum('purchase_quantity')
            )['total'] or 0

            # Check if new inventory amount is less than total purchase quantity
            if new_inventory_amount < total_purchase_quantity:
                messages.error(request, f"Inventory amount cannot be less than the total purchase quantity ({total_purchase_quantity}) for {inventory.item_name}.")
                return redirect('update_inventory', inventory_id = inventory_id)
            
            # Update remaining quantity as the difference between new inventory amount and total purchase quantity
            inventory.remaining_quantity = max(new_inventory_amount - total_purchase_quantity, 0)
            inventory.inventory_amount = new_inventory_amount

            # Save the inventory record
            inventory.save()

            # Trigger low inventory notification 
            if inventory.remaining_quantity <= 50:
                Notification.objects.create(
                    type='low_inventory',
                    message=f"Inventory for {inventory.item_name} is low: {inventory.remaining_quantity} remaining.",
                     triggered_by=request.user
                )
            
            return redirect('inventory_list')
    else:
        form = InventoryUpdateForm(instance=inventory)

    return render(request, 'members/update_inventory.html', {'form': form})

@login_required
def delete_inventory(request):
    if request.method == 'POST':
        inventory_ids = request.POST.getlist('inventories')
        Inventory.objects.filter(id__in=inventory_ids).delete()
        return redirect('inventory_list')  # Redirect to the inventory page after deletion
    

# Sales History CSV Export
@login_required
def export_sales_history(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Item Name', 'Purchase Quantity', 'Price Per Unit', 'Total Price', 'Purchase Date'])

    sales = Sale.objects.select_related('member')
    for sale in sales:
        writer.writerow([
            sale.member.first_name,
            sale.member.last_name,
            sale.item_name,
            sale.purchase_quantity,
            sale.price_per_unit,
            sale.total_price,
            sale.purchase_date
        ])

    return response

# Inventory CSV Export
@login_required
def export_inventory(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(['Item Name', 'Inventory Amount', 'Remaining Quantity'])

    inventories = Inventory.objects.all()
    for inventory in inventories:
        writer.writerow([
            inventory.item_name,
            inventory.inventory_amount,
            inventory.remaining_quantity
        ])

    return response

@login_required
def notifications(request):
    if request.user.is_superuser:
        notifications = Notification.objects.filter(is_read=False).order_by('-created_at')
    else:
        notifications = []

    return render(request, 'members/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if request.user.is_superuser:
        notification.is_read = True
        notification.save()
    return redirect('notifications')

@login_required
def inventory_recommendations(request):
    inventories = Inventory.objects.all()
    recommendations = []

    for inventory in inventories:
        # Calculate average monthly sales for each item
        sales = Sale.objects.filter(item_name=inventory.item_name)
        total_sales = sales.aggregate(Sum('purchase_quantity'))['purchase_quantity__sum'] or 0
        avg_sales = sales.aggregate(Avg('purchase_quantity'))['purchase_quantity__avg'] or 0

        # Define recommendation logic (i.e inventory should be twice the average sale)
        recommended_level = avg_sales * 2 if avg_sales else 100

        # Update inventory's recommended level
        inventory.recommended_inventory_level = recommended_level
        inventory.save()

        recommendations.append({
            'item_name': inventory.item_name,
            'inventory_amount': inventory.inventory_amount,
            'recommended_level': recommended_level,
            'remaining_quantity': inventory.remaining_quantity
        })

    return render(request, 'members/inventory_recommendations.html', {'recommendations': recommendations})

