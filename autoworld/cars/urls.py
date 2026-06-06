from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.CarsHome.as_view(), name='index'),
    path('category/<str:cat_slug>/', views.CategoryCarsPage.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', views.TagCarsPage.as_view(), name='tag'),
    path('categories/', views.CategoriesListPage.as_view(), name='categories_list'),
    path('tags/', views.TagsListPage.as_view(), name='tags_list'),
    path('cars/', views.CarsListPage.as_view(), name='cars_list'),
    path('brands/', views.BrandsListPage.as_view(), name='brands_list'),
    path('cars/<slug:brand_slug>/', views.BrandCarsPage.as_view(), name='brand'),
    path('car/<slug:car_slug>/', views.CarDetailPage.as_view(), name='car_detail'),
    path('car/<slug:car_slug>/comment/', views.AddCommentPage.as_view(), name='car_comment'),
    path('car/<slug:car_slug>/reaction/', views.ToggleReactionPage.as_view(), name='car_reaction'),
    path('comments/<int:comment_pk>/edit/', views.UpdateCommentPage.as_view(), name='comment_edit'),
    path('comments/<int:comment_pk>/delete/', views.DeleteCommentPage.as_view(), name='comment_delete'),
    path('car/<slug:car_slug>/edit/', views.UpdateCarPage.as_view(), name='car_edit'),
    path('car/<slug:car_slug>/delete/', views.DeleteCarPage.as_view(), name='car_delete'),
    path('vin/', views.VinInfoPage.as_view(), name='vin_check'),
    path('vin/<str:vin_code>/', views.VinInfoPage.as_view(), name='vin_check_result'),
    path('add-car/', views.AddCarModelPage.as_view(), name='add_car'),
    path('upload/', views.UploadFilePage.as_view(), name='upload_file'),
]
