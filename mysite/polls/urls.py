from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("user-input", views.UserInput.as_view(), name="userInput"), # form that takes user input into django db
    path("<int:question_id>/add-choice/", views.AddChoice.as_view(), name="addchoice"), # form that adds choices into existing questions in django db
    path("<int:question_id>/up-vote/", views.UpVote.as_view(), name="upvote"), # form that increases the vote of a particular question
    path("create-user", views.CreateUser.as_view(), name="newuser"), # form to create user
    path("login", views.LoginUser.as_view(), name="userlogin"), # form for existing user to login
    path("<int:question_id>/question-update/", views.QuestionUpdate.as_view(), name="updateQuestion"), #allow user to update question
    path("<int:question_id>/del-choice/", views.DelChoice.as_view(), name="delChoice"), # allow user to delete choice from a particular question
    path("admin-page", views.adminPage.as_view(), name="adminpg"),
    path("ajax-view", views.AjaxView.as_view(), name="AjaxView"),
]