import json

from django.http import JsonResponse
from django.shortcuts import render
from core.vector_db.chroma import delete_employee_collection, get_all_employees_from_vector_db
# Create your views here.
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from core.video.embedding import get_face_embedding
from user.utils import register_employee_face
from core.video.capture import convert_video_to_embedding
from core.vector_db.chroma import add_employee_to_vector_db,get_employee_from_vector_db
from .forms import LoginForm, RegisterForm
from .models import User

def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        # Face login path: if we have face_images
        if "face_images" in data:
            face_images = data.get("face_images") or []
            if not isinstance(face_images, list) or len(face_images) == 0:
                return JsonResponse({
                    "success": False,
                    "message": "No images provided."
                })
            print(type(face_images))
            print(face_images[0])
            # Now we must embed the images that we have received and compare them with the embeddings in the vector database. If we find a match, we will log the user in.
            face_embeddings = get_face_embedding(face_images)
            # we can now send te embedding to the vector DB to find a match. If we find a match, we will log the user in.
            get_employee_id=get_employee_from_vector_db(face_embeddings)
            if get_employee_id is None:
                return JsonResponse({
                                "success": True,
                                "message": "User Not Foundl."
                            })
            return JsonResponse({
                "success": True,
                "message": "User logged in successfully.",
                "employee_id": get_employee_id
            })
            # We get the id of the employee from the vector database. We will now use this id to get the user from the User model and log them in.
            # get_employee_object=User.objects.get(employee_id=get_employee_id)
            # #now we will log the user in by setting the session variable user_id to the id of the user object we just got from the User model. 
            # if get_employee_object:
            #     request.session["user_id"] = get_employee_object.id
            #     return JsonResponse({
            #         "success": True,
            #         "message": "User logged in successfully."
            #     })
        
        # WITHOUT RAG
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                user = User.objects.get(email=email)
                if check_password(
                    password,
                    user.password
                ):
                    request.session["user_id"] = user.id
                    return redirect("home")
                else:
                    form.add_error(
                        None,
                        "Invalid password"
                    )
            except User.DoesNotExist:
                form.add_error(
                    None,
                    "User does not exist"
                )
    else:
        form = LoginForm()
    return render(
        request,
        "user/login.html",
        {
            "form": form
        }
    )

def register_user(request):
    form=None
    employee_data={
        "employee_id": request.POST.get("employee_id"),
        "first_name": request.POST.get("first_name"),
        "last_name": request.POST.get("last_name"),
        "department": request.POST.get("department"),
        "designation": request.POST.get("designation")
    }
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        # Face login path: if we have face_images
        if "face_images" in data:
            face_images = data.get("face_images") or []
            if not isinstance(face_images, list) or len(face_images) == 0:
                return JsonResponse({
                    "success": False,
                    "message": "No images provided."
                })
            print(type(face_images))
            print(face_images[0])
            # Now we must embed the images that we have received and compare them with the embeddings in the vector database. If we find a match, we will log the user in.
            face_embeddings = get_face_embedding(face_images)
            # we can now send te embedding to the vector DB to find a match. If we find a match, we will log the user in.
            # get_employee = get_employee_from_vector_db(face_embeddings)
            add_employee_to_vector_db(employee_data, face_embeddings)
        form=RegisterForm(request.POST)
        if form.is_valid():
            employee_data={
                "employee_id": form.cleaned_data["employee_id"],
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "department": form.cleaned_data["department"],
                "designation": form.cleaned_data["designation"]
            }
            # We need to send the user data to the function convert_video_to_embedding to capture the video and get the embeddings. We will then save the embeddings in the vector database along with the user data.
            # convert_video_to_embedding(request=request, employee_data=employee_data)
            # frames = capture_face_frames()
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "user/register.html", {"form": form})

def empty_vector_database(request):
    # This function will empty the vector database. It will be used for testing purposes.
    delete_employee_collection()
    return JsonResponse({
        "success": True,
        "message": "Vector database emptied."
    })

def get_all_data(request):
    data=get_all_employees_from_vector_db()
    print(f"Data from vector database: {data}")
    return JsonResponse({
        "success": True,
        "data": data
    })