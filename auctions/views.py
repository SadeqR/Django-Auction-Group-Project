from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Auction, Bid, Comment
from .forms import AddBidForm, AddAuctionForm
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    DeleteView
)

## HOME PAGE - LIST
class AuctionListView(ListView):
    model = Auction
    template_name = 'auctions/home.html'
    # order by newest auctions
    ordering = ['-date_created']
    # amount of pagination per page
    paginate_by = 5
    def get(self, request):
        checkAuctions()

        ctx = {}
        url_parameter = request.GET.get("q")

        # filter for the AJAX call here...
        if url_parameter:
            auctions = Auction.objects.filter(title__icontains=url_parameter).filter(closed=False).order_by('-date_created')
        else:
            auctions = Auction.objects.filter(closed=False).order_by('-date_created')
        
        # store 'items' into context with a list of auctions above
        ctx["items"] = auctions

        # if this is a ajax request, give the new html to render, with the auctions passed in
        if request.is_ajax():
            html = render_to_string(
                template_name="auctions/auctions-results-partial.html", context={"items": auctions}
            )
            data_dict = {"the_html_v": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, "auctions/home.html", context=ctx)

## Show users auctions when clicking on the user on an auction
class UserAuctionListView(ListView):
    model = Auction
    template_name = 'accounts/account_auctions.html'
    # match the items passed in (all the auction objects)
    context_object_name = 'items'
    # amount of pagination per page
    paginate_by = 5
    def get_queryset(self):
        checkAuctions()
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Auction.objects.filter(owner=user).order_by('-date_created')


# Show the history of bids
class BidDetailView(DetailView):
    model = Auction
    template_name = 'auctions/bid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checkAuctions()
        auction = get_object_or_404(Auction, pk=self.kwargs.get('pk'))
        context['bid_list'] = Bid.objects.filter(auction=auction).order_by('date_created')
        return context

# calculating how to increment prices on bids i.e 10 => increase by 1, 100 => increase by 10 etc
def getPercents(auction):
    percents = "1"
    increment = len(str(auction.price)) - 1
    print(increment)
    for a in range(increment-1):
        percents = percents + "0"
    percents = int(percents)
    return percents

# Show the auction details
class AuctionDetailView(FormMixin, DetailView):
    model = Auction
    form_class = AddBidForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        checkAuctions()
        context = super().get_context_data(**kwargs)
        auction = get_object_or_404(Auction, pk=self.kwargs.get('pk'))
        context['bid_list'] = Bid.objects.filter(auction=auction).order_by('date_created')
        if len(context['bid_list']) <= 0:
            price = auction.price + getPercents(auction)
        else:
            price = context['bid_list'].last().price + getPercents(auction)
        context['form'] = AddBidForm(initial={
            'auction': self.object,
            'price' : price,
            'user': self.request.user,
        })
        # Pass the comments that this auction has attached and order by the date created
        context['comments'] = Comment.objects.filter(auction_id=self.object).order_by('date_created')
        return context
        
    def post(self, request, *args, **kwargs):

        # other form was asked such as bidding into the page...
        

        # a comment was sent to the owner, create a comment object and save it
        if request.method == 'POST':
            if request.POST.get("comment"):
                msg = Comment()
                msg.user = self.request.user
                msg.auction = self.get_object()
                msg.message = self.request.POST.get("comment")
                msg.date_created = timezone.now()
                msg.save()
        
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            print("form was valid!")
            return self.form_valid(form)
        else:
            print("form wasn't valid!")
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.auction = self.object
        form.instance.price = self.request.POST.get("price")
        self.object.price = form.instance.price
        self.object.amount_of_bids = self.object.amount_of_bids + 1
        self.object.save()
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

## CREATE
class AuctionCreateView(LoginRequiredMixin, CreateView):
    model = Auction
    form_class = AddAuctionForm

    #override form_valid
    def form_valid(self, form):
        checkAuctions()
        # take author as the current loggged in user
        form.instance.owner = self.request.user
        return super().form_valid(form)

## UPDATE
class AuctionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Auction
    fields = ['title', 'description', 'condition', 'image']

    #override form_valid
    def form_valid(self, form):
        # take author as the current loggged in user
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        checkAuctions()
        auction = self.get_object()
        # check if the current user is the owner
        return self.request.user == auction.owner

## DELETE
class AuctionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Auction
    success_url = '/'

    def test_func(self):
        auction = self.get_object()
        # check if the current user is the owner
        return self.request.user == auction.owner


# Show about.html
def about(request):
    checkAuctions()
    return render(request, 'auctions/about.html', {'title' : 'About'})

# Show closed auction objects in to closed.html page
class ClosedAuctionsListView(ListView):
    # order by newest auctions
    ordering = ['-date_created']
    template_name = "auctions/closed.html"
    # amount of pagination per page
    paginate_by = 5
    context_object_name = 'items'
    def get_queryset(self):
        checkAuctions()
        return Auction.objects.filter(closed=True)


# This gets called whenever we want to check the auctions if theyre closed or finished etc..
def checkAuctions():
    auctions = Auction.objects.all()
    bids = Bid.objects.all()
    valid_auctions = []
    sendMail = False
    subject = ""
    message = ""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ["",]
    for auc in auctions:
        if auc.expired and auc.closed == False:
            auc.closed = True
            # Set the last bid on here to maxed out and save it into auction
            last_bid = bids.filter(auction=auc).last()
            if last_bid is not None:
                auc.winnerBid = last_bid
                last_bid.winningBid = True
                last_bid.save()
                sendMail = True
            auc.save()
            # Sending the user email when they have won
            if sendMail:
                    subject = 'Won auction - ' + str(auc.title)
                    message = 'Congratulations on winning the auction titled ' + str(auc.title) + " please pay the user " + str(auc.owner.username) + ", the sum of £" + str(auc.price) + "."

                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [last_bid.user.email,]
                    try:
                        send_mail( subject, message, email_from, recipient_list )
                    except:
                        pass
        else:
            valid_auctions.append(auc)
    
    return valid_auctions