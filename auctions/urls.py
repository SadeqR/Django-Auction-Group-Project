from django.urls import path
from . views import (
    AuctionListView, 
    AuctionDetailView, 
    AuctionCreateView,
    AuctionUpdateView,
    AuctionDeleteView,
    UserAuctionListView,
    BidDetailView,
    ClosedAuctionsListView,
)
from . import views


urlpatterns = [
    path('', AuctionListView.as_view(), name='auction-home'),
    path('account/<str:username>', UserAuctionListView.as_view(), name='account-auctions'),
    path('auction/<int:pk>/', AuctionDetailView.as_view(), name='auction-detail'),
    path('auction/<int:pk>/bids/', BidDetailView.as_view(), name='auction-bid'),
    path('auction/create/', AuctionCreateView.as_view(), name='auction-create'),
    path('auction/<int:pk>/update/', AuctionUpdateView.as_view(), name='auction-update'),
    path('auction/<int:pk>/delete/', AuctionDeleteView.as_view(), name='auction-delete'),
    path('about/', views.about, name='auction-about'),
    path('closedAuctions/', ClosedAuctionsListView.as_view(), name='auction-closed'),
]