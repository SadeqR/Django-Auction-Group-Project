from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, UpdateProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from auctions.models import Auction
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save() 
            # creates the user object in the table
            username = form.cleaned_data.get('username')
            messages.success(request, f'Acccount created for {username}!')
            return redirect('login')
    else:
        # registration form inbuilt django
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

# decorator to make sure user is logged in
@login_required
def profile(request):
    if request.method == 'POST':
        updateUserForm = UserUpdateForm(request.POST, instance=request.user)
        updateProfileForm = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        # save profiles if valid
        if updateUserForm.is_valid() and updateProfileForm.is_valid():
            updateUserForm.save()
            updateProfileForm.save()
            messages.success(request, f'Acccount updated!')
            return redirect('profile')
    else:
        updateUserForm = UserUpdateForm(instance=request.user)
        updateProfileForm = UpdateProfileForm(instance=request.user.profile)

    # Pass all auctions that I won here...

    # First find all those that are closed
    auctions = Auction.objects.filter(closed=True)
    # Now find the winningBid is equal to me
    myWins = []
    for aucs in auctions:
        # Are there any winning bids on this auction?
        if aucs.winnerBid:
            # Am i the winning bid?
            if aucs.winnerBid.user == request.user:
                myWins.append(aucs)

    context = {
        'updateUserForm' : updateUserForm,
        'updateProfileForm' : updateProfileForm,
        'myWins' : myWins
    }

    return render(request, 'accounts/profile.html', context)