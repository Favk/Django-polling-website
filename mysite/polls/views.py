from typing import Any, Dict
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from .models import Choice, Question

User = get_user_model() # create user model and import it

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

#decorating this view
@method_decorator(login_required, name="dispatch")    #cannot access form without being logged in into django admin, redirects user to login page
class UserInput(generic.View):
    template_name = "polls/view.html"

    def get(self, request):# get request from the form
        return render(request, self.template_name)
    
    def post(self, request):
        question = request.POST["question"] #get the question from the form
        #pubDate = request.POST["date"] # get publishing date

        Question.objects.create(question_text = question)
        return render(request, self.template_name)
    

@method_decorator(login_required, name="dispatch")
class AddChoice(generic.ListView):
    template_name = "polls/rand.html"
    context_object_name = "choices" # to get choice from choices

    def get_queryset(self):
        q_id = self.kwargs["question_id"]
        question = Question.objects.get(id = q_id)
        return Choice.objects.filter(question = question)
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        qId = self.kwargs["question_id"]
        context["question_id"] = qId
        return context
    
    def post(self, request, *args, **kwargs):
        data = request.POST # gets dictionary of user input
        q_id = self.kwargs["question_id"]
        qn = Question.objects.get(id = q_id)
        Choice.objects.create(question=qn, choice_text=data["choice"])# to actually add a choice to the database
        return self.get(request, *args, **kwargs)

    
class UpVote(generic.DetailView):
    template_name = "polls/db.html"
    context_object_name = "question" # to get choices from questions

    def get_queryset(self):
        return Question.objects.all() # returns all data in question
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        qId = self.get_object()
        context["choices"] = Choice.objects.filter(question = qId)
        return context # we get the data of the select question id
    
    def get_object(self):
        query_set = self.get_queryset()
        qId = self.kwargs["question_id"]
        return query_set.get(id = qId)    # get the question id

    def post(self, request, *args, **kwargs):
        data = request.POST
        choice_id = data.get("choice")
        cId = Choice.objects.get(id=choice_id)
        cId.votes += 1
        cId.save()
        return self.get(request, *args, **kwargs)

  
class CreateUser(generic.View):
    template_name = "polls/auth.html"

    def get(self, request):
        return render(request, self.template_name) # see authentication form that gets user info
    
    def post(self, request):
        data = request.POST
        FirstName = data.get("f_name") # get user first name from auth form
        LastName = data.get("l_name") # get user last name from auth form
        UserName = data.get("username") # get user username from auth form
        Pwd = data.get("password") # get user password from auth form

        user_info = User.objects.create(first_name=FirstName, last_name=LastName, username=UserName) # add fields to user model and saving it
        user_info.set_password(Pwd) # set password
        user_info.save() # save info to database

        messages.success(request, "Congratulaions, you are now a user")
        return render(request, self.template_name)
    

class LoginUser(generic.View):
    template_name = "polls/login.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        data = request.POST
        user_name = data.get("user_name")
        passwd = data.get("password")

        user = authenticate(request, username = user_name, password = passwd)
        if user is not None:
            login(request, user)
            return redirect("polls:index") # returns polls main page
        else:
            messages.error(request, "User could not log in. PLease try again")

        return render(request, self.template_name)


@method_decorator(login_required, name="dispatch")
class QuestionUpdate(generic.DetailView):
    template_name = "polls/question.html"
    context_object_name = "question"

    def get_queryset(self):
        return Question.objects.all() # returns all data in question
    
    def get_object(self):
        query_set = self.get_queryset()
        qId = self.kwargs["question_id"]
        return query_set.get(id = qId)    # get the question id
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        qId = self.get_object()
        context["choices"] = Choice.objects.filter(question = qId)
        return context # we get the data of the select question id
    
    def post(self, request, *args, **kwargs):
        data = request.POST # gets dictionary of user input
        q_id = self.kwargs["question_id"]
        # first method. updates 1 record at at time
        qn = Question.objects.get(id = q_id)
        qn.question_text = data["qtext"]
        qn.save()

        #another method, can update multiple records
        # Question.objects.filter(id=q_id).update(question_text=data["question"])
        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class DelChoice(generic.ListView):
    template_name = "polls/delchoice.html"
    context_object_name = "choices"
    
    def get_question(self):
        return Question.objects.get(id=self.kwargs["question_id"])

    def get_queryset(self):
        question = self.get_question()
        return Choice.objects.filter(question=question) # returns all data in question
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        Choice.objects.filter(id=data["choice"]).delete() #FILTER BEFORE DELETE #filter choice you want by id, and then delete said choice
        return self.get(request, *args, **kwargs)


class adminPage(generic.View):
    template_name = "polls/admin.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        data = request.POST
        user_name = data.get("user_name")
        passwd = data.get("pwd")

        user = authenticate(request, username = user_name, password = passwd)
        if user is not None:
            login(request, user)
            return redirect("polls:index") # returns polls main page
        else:
            messages.error(request, "User could not log in. PLease try again")

        return render(request, self.template_name)

class AjaxView(generic.View):        
    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        if data["request_type"] == "delete_question": # if delete question
            Question.objects.get(id=data["question"]).delete() # delete said question
        return JsonResponse({'status':'success'})

#secure route to pages
#using method_decorator(login_required, name="dispatch")

# Sessions
# update questions and delete choices
# create html for them


# create log out route in all protected pages, a button that states log out on all pages
# make all update buttons in for each question 

# before question list, create question button to add question at the top of the list
# admin log in and sees questions and beside the questions, you see 3 buttons for edit(update, delete) questions, edit choices, view choice
# when update question, go to update question route for that particular question
# when delete question, go to update question route for that particular question
# when view choices, shows a list of choces for particular question ; have buttons, delete choice and update choice ; before list begins, add choice button to add choice at top of list

# use bootstrap 4 to make pages pretty and jquery

# make HTML templates for admin homepage

# 18/12/23
# writing a func in js to do the action we want

'''
Authentication: you need to create a way to register new members
First, last names, username password to create new users

User models: django has for you
django.contrib.auth import get_user_model (function)
User = get_user_model() 'model user'
has fields first_name, last_name, username, email, is_active, is_superuser(can log into admin), password(hashed password), is_staff(if true, can log into django admin)

Difference btween superuser and staff
Superuser assigns permissions to staff

password
don't create user object with password, don't pass it in create method
user1.set_passowrd(password)
user1.save()


log-in
collect username and password from user


'''