from django.shortcuts import render,redirect
from django.http import HttpResponse ##used for direct returning the html tags.
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from home.models import *
from django.contrib import messages
from django.db import IntegrityError
from home.decorators import custom_login_required
import random
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json
from home.utils import save_data_to_files,DataProcess,perform_computation
from copy import deepcopy
import pandas as pd
import math
import re
from django.views.decorators.csrf import csrf_protect
import numpy as np
from django.core.mail import send_mail
from django.utils import timezone
import os
import jwt
from datetime import timedelta, datetime
from core.settings import SECRET_KEY,DEFAULT_FROM_EMAIL,BASE_DIR, STATIC_URL


truck_specs = {
    "General Purpose container 20'": {
        "length_container":5900,
        "width_container":2352,
        "height_container":2393,
        "max_weight": 32500,
        # Add more specifications as needed
    },
    "General Purpose container 40'": {
        "length_container":12032,
        "width_container":2352,
        "height_container":2395,
        "max_weight": 32500,
        # Add more specifications as needed
    },
    "High - Cube General Purpose container 40'": {
        "length_container":12032,
        "width_container":2432,
        "height_container":2700,
        "max_weight": 32500,
    },
    # Add more specifications as needed
}
# SECRET_KEY = settings.SECRET_KEY 
def generate_jwt_token(email_id,userType,company):
    expiration_time = datetime.utcnow() + timedelta(hours=5)
    payload = {
        'email': email_id,
        'userType':userType,
        "company":company,
        'exp': expiration_time  # Expiration time for the token
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrftoken': csrf_token})
    
def generate_unique_user_id():
    while True:
        # Generate a random six-digit number
        random_id = random.randint(100000, 999999)
        
        # Check if the random_id is unique in the Users model
        if not Users.objects.filter(user_id=random_id).exists():
            return random_id

def home(request):
    return render(request, "home.html")

def freeTrial(request):
    return render(request, 'freeTrial.html')

def joinCreateOrganisation(request):
    return render(request, 'loginSignup.html')  # Assuming this is your join/create organisation template

def additionalInformation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_name = request.POST.get('company-name')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'additionalInformation.html')

        company, created = Company.objects.get_or_create(company_name=company_name)

        if created and not company.company_code:
            company.company_code = company.generate_unique_code()
            company.save()

        # Check if a user with the provided email already exists
        user_exists = Users.objects.filter(email_id=email).exists()
        if user_exists:
            messages.error(request, "An account with this email already exists.")
            return render(request, 'login.html')

        # Create a new user
        user = Users(
            email_id=email,
            user_id=generate_unique_user_id(),
            user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
            user_last_name='DefaultLastName',    # Replace with actual form data or defaults
            user_type='Company_loader',          # Replace with actual logic for user type
            user_status='Active',
            is_authenticated=True,
            company=company                      # Associate with the created or retrieved company
        )

        user.set_password(password)
        user.save()

        # Authenticate and log the user in
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            # Redirect to the dashboard after successful login
            return redirect('dashboard')
        else:
            messages.error(request, "Authentication failed. Please try logging in again.")
            return redirect('login')  # Redirect to login if authentication fails

    return render(request, 'additionalInformation.html')  # Render additional information form for GET request

def additionalInformationJson(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return JsonResponse({"ERROR": "Email and password are required."}, status=400)

        company, created = Company.objects.get_or_create(company_name=company_name)

        if created and not company.company_code:
            company.company_code = company.generate_unique_code()
            company.save()

        # Check if a user with the provided email already exists
        user_exists = Users.objects.filter(email_id=email).exists()
        if user_exists:
            messages.error(request, "An account with this email already exists.")
            return JsonResponse({"ERROR": "An account with this email already exists."}, status=400)

        # Create a new user
        user = Users(
            email_id=email,
            user_id=generate_unique_user_id(),
            user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
            user_last_name='DefaultLastName',    # Replace with actual form data or defaults
            user_type='Company_loader',          # Replace with actual logic for user type
            user_status='Active',
            is_authenticated=True,
            company=company                      # Associate with the created or retrieved company
        )

        user.set_password(password)
        user.save()

        # Authenticate and log the user in
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            # Redirect to the dashboard after successful login
            return JsonResponse({"SUCCESS": "User login successfully"}, status=200)
        else:
            messages.error(request, "Authentication failed. Please try logging in again.")
            return JsonResponse({"ERROR": "Authentication failed. Please try logging in again."}, status=400)

    return JsonResponse({"SUCCESS": "Signup successfully"}, status=200)
  

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            user.is_authenticated= True
            user.save()
            # next_url = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if 'next' is not provided
            return redirect(dashboard)  # Use the 'next' parameter if available
        else:
            return redirect('additionalInformation')

    return render(request, 'login.html')  # Render the login template in case of GET request or errors
def login_viewJson(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return JsonResponse({"ERROR": "Email and password are required."}, status=400)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            user.is_authenticated= True
            user.save()
            # next_url = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if 'next' is not provided
            return JsonResponse({"SUCCESS": "Signup successfully"}, status=200)
        else:
            return JsonResponse({"ERROR": "Authentication failed. Please try logging in again."}, status=400)

    return JsonResponse({"SUCCESS": "Login successfully"}, status=200)


@custom_login_required
def dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'dashboard.html', context)

@custom_login_required
def profile(request):
    context = {
        'user': request.user,
        'utilization_range': range(70, 96,5),
        'delivery_horizon_range': range(1, 21,3),
    }
    return render(request, 'profile.html',context)

def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        # Set custom authenticated field to False
        user.is_authenticated = False
        user.save()  # Save the updated authentication status in the database
        
        logout(request)  # This will clear the session and log the user out
    return redirect(home)

def enquire(request):
    return render(request, 'enquiry.html')
@csrf_exempt
def add_container(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        length = data.get('containerLength')
        width = data.get('containerWidth')
        height = data.get('containerHeight')
        max_weight = data.get('maxWeight')

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@custom_login_required
def manageUsers(request):
    return render(request, 'manageUsers.html')
@csrf_exempt
def freeOutput(request):
    if request.method == 'POST':
        num_types = request.POST.get('numTypes')
        total_containers = request.POST.get('totalContainers')
        num_containers = int(request.POST.get('numContainers'))
        # print(num_types)

        # print("num_c",num_containers)

        # Collect box details
        box_details = []
        for i in range(int(num_types)):
            box = {
                'Gross Weight (in KGs)': request.POST.get(f'grossWeight{i}'),
                'Net Weight (in KGs)': request.POST.get(f'netWeight{i}'),
                'Volume (in m^3)': request.POST.get(f'volume{i}'),
                'Temperature (in deg  C)': request.POST.get(f'temperature{i}'),
                'Length (in mm)': request.POST.get(f'length{i}'),
                'Width (in mm)': request.POST.get(f'width{i}'),
                'Height (in mm)': request.POST.get(f'height{i}'),
                'Number of Cases': request.POST.get(f'numberOfCases{i}'),
                'Rotation Allowed (1 - YES, 0 - NO)': 1 if request.POST.get(f'rotationAllowed{i}') == 'on' else 0,
                'color': request.POST.get(f'color{i}')
            }
            box_details.append(box)

        # Create DataFrame

        def rgba_string_to_hex(rgba_string):
            # Use regex to extract RGBA values from the string
            match = re.match(r'rgba\((\d+(\.\d+)?),\s*(\d+(\.\d+)?),\s*(\d+(\.\d+)?),\s*([0-1](\.\d+)?)\)', rgba_string)
            
            if not match:
                raise ValueError("Invalid RGBA string format")
            
            # Extracting the values and converting them to float
            r, g, b, a = map(float, [match.group(1), match.group(3), match.group(5), match.group(7)])
            
            # Ensure that RGB values are within the valid range [0, 255]
            r = int(max(0, min(255, r)))
            g = int(max(0, min(255, g)))
            b = int(max(0, min(255, b)))
            
            # Convert RGB to hex
            hex_color = f'#{r:02X}{g:02X}{b:02X}'
            
            # If alpha is not 1, include it in the hex code
            if a < 1.0:
                a = int(a * 255)
                hex_color += f'{a:02X}'
            
            return hex_color

        df = pd.DataFrame(box_details)
        for i in range(len(df['color'])):
            df.loc[i,'color']= rgba_string_to_hex(df['color'][i])

        # Collect container details
        # print(df)
        container_data = {}
        for i in range(int(total_containers)):
            container_type = request.POST.get(f'containerType{i+1}')
            # if container_type == "Custom Container":
            #     container = {
            #         'type': container_type,
            #         'length': request.POST.get('customLength'),
            #         'width': request.POST.get('customWidth'),
            #         'height': request.POST.get('customHeight'),
            #         'max_capacity': request.POST.get('customMaxCapacity')
            #     }
            # else:
            #     container = {'type': container_type}
            # container_details.append(container)
            if container_type == "Custom Container":
                custom_length = int(request.POST.get('customLength'))
                custom_width = int(request.POST.get('customWidth'))
                custom_height = int(request.POST.get('customHeight'))
                custom_max_weight = int(request.POST.get('customMaxWeight'))
                truck_specs["Custom Container"] = {
                    'length_container': custom_length,
                    'width_container': custom_width,
                    'height_container': custom_height,
                    'max_weight': custom_max_weight
                }
            container_count = len(total_containers)
            container_data[container_type] = num_containers

        # print(truck_specs)
        # print(container_data)
        # container_data = {}

        # for i in range(1, total_containers + 1):
        #     container_type = request.POST[f'containerType{i}']
        #     if container_type == "Custom Container":
        #         custom_length = int(request.POST['customLength'])
        #         custom_width = int(request.POST['customWidth'])
        #         custom_height = int(request.POST['customHeight'])
        #         custom_max_weight = int(request.POST['customMaxWeight'])
        #         truck_specs["Custom Container"] = {
        #             'length_container': custom_length,
        #             'width_container': custom_width,
        #             'height_container': custom_height,
        #             'max_weight': custom_max_weight
        #         }
        #     container_count = int(request.POST[f'containerCount{i}'])
        #     container_data[container_type] = container_count

        # df = pd.read_excel(file)
        save_data_to_files(df, container_data)  # Assuming you have a function for this
        data = deepcopy(df)
        df_storer = []
        img_paths = []
        threed_boxes= []
        container_list = []
        packd_list = []
        sku_info = []
        vol_curr_list = []
        perc_wasted_list = []
        vol_container_list = []
        num_placed = [0]*len(df)
        outer_index = 0
        box_info =  []
        rem_Strip_calc = []
        rem_boxes= []
        # df.index += 1
        
        


        for keys, values in container_data.items():
            selected_truck_spec = truck_specs.get(keys, {})
            if outer_index == 0:
                df, container_toFit, strip_list = DataProcess(df, selected_truck_spec, 1, 1, data)
                for i in range(len(df)):
                    rem_Strip_calc.append(df['Rem_Strips'][i])
                    rem_boxes.append(df['Rem_Boxes'][i])
                
            else:
                df, container_toFit, strip_list = DataProcess(df, selected_truck_spec, 1, 2, data)

            roll = values
            # print(df)

            index_ = 0
            prev = -1
            while roll > 0:
                filename, df,packaging_density,vol_occ_curr,perc_wasted,vol_container,box_coords, container_inf = perform_computation(df, container_toFit, strip_list, keys, index_)
                curr = []
                # num_placed.append((df['TotalNumStrips'][index_]-df['Rem_Strips'][index_])*df['NumOfBoxesPerStrip'][index_])
                for i in range(len(df)):
                    # print(df)
                    # if(prev==-1):
                    #     prev = df['Rem_Strips'][i]
                    #     num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i]
                   
                    
                    # if(prev!=df['Rem_Strips'][i] and df['Rem_Strips'][i]!=0):
                    #     num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i]
                    # box_info.append()
                    # if roll == 1:
                    #     curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + rem_boxes[i])
                    # else:   
                    #     curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i])
                    if df['Rem_Boxes'][i] != rem_boxes[i]:
                        curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + rem_boxes[i])
                        rem_boxes[i] = 0
                    else:
                        curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i])

                        
                    rem_Strip_calc[i] = df['Rem_Strips'][i]
                    # num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + df['Rem_Boxes'][i]
                box_info.append(curr)
                
                packaging_density = math.trunc(packaging_density*100)
                # print(packaging_density)
                vol_occ_curr = round(vol_occ_curr, 3)
                perc_wasted = round(perc_wasted, 3)
                vol_container = round(vol_container*pow(10,-9), 3)

                packd_list.append(packaging_density)
                vol_curr_list.append(vol_occ_curr)
                perc_wasted_list.append(perc_wasted)
                vol_container_list.append(vol_container)
                threed_boxes.append(box_coords)
                container_list.append(container_inf)
                df_storer.append(df.to_html(classes='data'))
                index_ += 1
                roll -= 1
                img_paths.append(filename)

            outer_index += 1

        # print(img_paths)
        
        # container_count = len(total_containers)  # Number of containers
        # print(df)
        distinct_colors = df['Color'].tolist()
        for i in range(len(df)):
            sku_info.append([
                df['BoxNumber'][i]+1,
                df['Length'][i],
                df['Width'][i],
                df['Height'][i],
                df['NumOfBoxesPerStrip'][i]
            ])
        # print(box_info)

        df_ht= df.drop(['BoxNumber','TotalNumStrips','Rem_Boxes','Rem_Strips','Alpha(rotation about Z-axis)','GrossWeight','Marked','Color'],axis=1)
        df_ht.index+=1
        # print(df_ht)
        df_ht = df_ht.to_html(classes='data')
        container_indices = range(1,num_containers+1)
        # print(threed_boxes)
        # print(container_inf)
        context = {
            'packaging_density': packd_list,
            'vol_occ_curr': vol_curr_list,
            'vol_container':vol_container_list,
            'container_type' : container_type,
            'container_indices' : container_indices,
            'threed_paths': threed_boxes,
            'container_inf' : container_list,
            'num_skus': range(1,len(df)+1),
            'colors' : distinct_colors,
            'sku_info':sku_info,
            'box_info':box_info,
            'df':df_ht
            
        }
        # print(context)
        # print(num_placed)
        return render(request, 'freeOutput.html', context)  # Redirect to a success page
    return render(request, 'freeOutput.html')
@csrf_exempt
def freeOutputJson(request):
    if request.method == 'POST':
        num_types = request.POST.get('numTypes')
        total_containers = request.POST.get('totalContainers')
        num_containers = int(request.POST.get('numContainers'))
        # print(num_types)

        # print("num_c",num_containers)
        print(request.POST)

        # Collect box details
        box_details = []
        for i in range(int(num_types)):
            box = {
                'Gross Weight (in KGs)': request.POST.get(f'grossWeight{i}'),
                'Net Weight (in KGs)': request.POST.get(f'netWeight{i}'),
                'Volume (in m^3)': request.POST.get(f'volume{i}'),
                'Temperature (in deg  C)': request.POST.get(f'temperature{i}'),
                'Length (in mm)': request.POST.get(f'length{i}'),
                'Width (in mm)': request.POST.get(f'width{i}'),
                'Height (in mm)': request.POST.get(f'height{i}'),
                'Number of Cases': request.POST.get(f'numberOfCases{i}'),
                'Rotation Allowed (1 - YES, 0 - NO)': 1 if request.POST.get(f'rotationAllowed{i}') == 'on' else 0,
                'color': request.POST.get(f'color{i}')
            }
            box_details.append(box)

        # Create DataFrame

        def rgba_string_to_hex(rgba_string):
            # Use regex to extract RGBA values from the string
            match = re.match(r'rgba\((\d+(\.\d+)?),\s*(\d+(\.\d+)?),\s*(\d+(\.\d+)?),\s*([0-1](\.\d+)?)\)', rgba_string)
            
            if not match:
                raise ValueError("Invalid RGBA string format")
            
            # Extracting the values and converting them to float
            r, g, b, a = map(float, [match.group(1), match.group(3), match.group(5), match.group(7)])
            
            # Ensure that RGB values are within the valid range [0, 255]
            r = int(max(0, min(255, r)))
            g = int(max(0, min(255, g)))
            b = int(max(0, min(255, b)))
            
            # Convert RGB to hex
            hex_color = f'#{r:02X}{g:02X}{b:02X}'
            
            # If alpha is not 1, include it in the hex code
            if a < 1.0:
                a = int(a * 255)
                hex_color += f'{a:02X}'
            
            return hex_color

        df = pd.DataFrame(box_details)
        for i in range(len(df['color'])):
            df.loc[i,'color']= rgba_string_to_hex(df['color'][i])

        # Collect container details
        print(df.columns)
        container_data = {}
        for i in range(int(total_containers)):
            container_type = request.POST.get(f'containerType{i}')
            # if container_type == "Custom Container":
            #     container = {
            #         'type': container_type,
            #         'length': request.POST.get('customLength'),
            #         'width': request.POST.get('customWidth'),
            #         'height': request.POST.get('customHeight'),
            #         'max_capacity': request.POST.get('customMaxCapacity')
            #     }
            # else:
            #     container = {'type': container_type}
            # container_details.append(container)
            if container_type == "Custom Container":
                custom_length = int(request.POST.get('customLength'))
                custom_width = int(request.POST.get('customWidth'))
                custom_height = int(request.POST.get('customHeight'))
                custom_max_weight = int(request.POST.get('customMaxWeight'))
                truck_specs["Custom Container"] = {
                    'length_container': custom_length,
                    'width_container': custom_width,
                    'height_container': custom_height,
                    'max_weight': custom_max_weight
                }
            container_count = len(total_containers)
            container_data[container_type] = num_containers

        # print(truck_specs)
        # print(container_data)
        # container_data = {}

        # for i in range(1, total_containers + 1):
        #     container_type = request.POST[f'containerType{i}']
        #     if container_type == "Custom Container":
        #         custom_length = int(request.POST['customLength'])
        #         custom_width = int(request.POST['customWidth'])
        #         custom_height = int(request.POST['customHeight'])
        #         custom_max_weight = int(request.POST['customMaxWeight'])
        #         truck_specs["Custom Container"] = {
        #             'length_container': custom_length,
        #             'width_container': custom_width,
        #             'height_container': custom_height,
        #             'max_weight': custom_max_weight
        #         }
        #     container_count = int(request.POST[f'containerCount{i}'])
        #     container_data[container_type] = container_count

        # df = pd.read_excel(file)
        save_data_to_files(df, container_data)  # Assuming you have a function for this
        data = deepcopy(df)
        df_storer = []
        img_paths = []
        threed_boxes= []
        container_list = []
        packd_list = []
        sku_info = []
        vol_curr_list = []
        perc_wasted_list = []
        vol_container_list = []
        num_placed = [0]*len(df)
        outer_index = 0
        box_info =  []
        rem_Strip_calc = []
        rem_boxes= []
        # df.index += 1
        
        


        for keys, values in container_data.items():
            selected_truck_spec = truck_specs.get(keys, {})
            if outer_index == 0:
                df, container_toFit, strip_list = DataProcess(df, selected_truck_spec, 1, 1, data)
                for i in range(len(df)):
                    rem_Strip_calc.append(df['Rem_Strips'][i])
                    rem_boxes.append(df['Rem_Boxes'][i])
                
            else:
                df, container_toFit, strip_list = DataProcess(df, selected_truck_spec, 1, 2, data)

            roll = values
            # print(df)

            index_ = 0
            prev = -1
            while int(roll) > 0:
                filename, df,packaging_density,vol_occ_curr,perc_wasted,vol_container,box_coords, container_inf = perform_computation(df, container_toFit, strip_list, keys, index_)
                curr = []
                # num_placed.append((df['TotalNumStrips'][index_]-df['Rem_Strips'][index_])*df['NumOfBoxesPerStrip'][index_])
                for i in range(len(df)):
                    # print(df)
                    # if(prev==-1):
                    #     prev = df['Rem_Strips'][i]
                    #     num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i]
                   
                    
                    # if(prev!=df['Rem_Strips'][i] and df['Rem_Strips'][i]!=0):
                    #     num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i]
                    # box_info.append()
                    # if roll == 1:
                    #     curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + rem_boxes[i])
                    # else:   
                    #     curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i])
                    if df['Rem_Boxes'][i] != rem_boxes[i]:
                        curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + rem_boxes[i])
                        rem_boxes[i] = 0
                    else:
                        curr.append((rem_Strip_calc[i] - df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i])

                        
                    rem_Strip_calc[i] = df['Rem_Strips'][i]
                    # num_placed[i] = (df['TotalNumStrips'][i]-df['Rem_Strips'][i])*df['NumOfBoxesPerStrip'][i] + df['Rem_Boxes'][i]
                box_info.append(curr)
                
                packaging_density = math.trunc(packaging_density*100)
                # print(packaging_density)
                vol_occ_curr = round(vol_occ_curr, 3)
                perc_wasted = round(perc_wasted, 3)
                vol_container = round(vol_container*pow(10,-9), 3)

                packd_list.append(packaging_density)
                vol_curr_list.append(vol_occ_curr)
                perc_wasted_list.append(perc_wasted)
                vol_container_list.append(vol_container)
                threed_boxes.append(box_coords)
                container_list.append(container_inf)
                df_storer.append(df.to_html(classes='data'))
                index_ += 1
                roll -= 1
                img_paths.append(filename)

            outer_index += 1

        # print(img_paths)
        
        # container_count = len(total_containers)  # Number of containers
        # print(df)
        distinct_colors = df['Color'].tolist()
        for i in range(len(df)):
            sku_info.append([
                df['BoxNumber'][i]+1,
                df['Length'][i],
                df['Width'][i],
                df['Height'][i],
                df['NumOfBoxesPerStrip'][i]
            ])
        # print(box_info)

        df_ht= df.drop(['BoxNumber','TotalNumStrips','Rem_Boxes','Rem_Strips','Alpha(rotation about Z-axis)','GrossWeight','Marked','Color'],axis=1)
        df_ht.index+=1
        # print(df_ht)
        df_ht = df_ht.to_html(classes='data')
        container_indices = range(1,num_containers+1)
        # print(threed_boxes)
        # print(container_inf)
    threed_data = []
    # base_dir = r'home\static\files'
    base_dir = BASE_DIR
    for path in threed_boxes:
        full_path = os.path.join(base_dir, STATIC_URL, os.path.basename(path))
        try:
            with open(full_path, 'r') as file:
                threed_data.append(json.load(file))
        except FileNotFoundError:
            return JsonResponse({"error": f"File not found: {full_path}"}, status=404)
    containerList = []
    for path in container_list:
        full_path = os.path.join(base_dir, STATIC_URL, os.path.basename(path))
        try:
            with open(full_path, 'r') as file:
                containerList.append(json.load(file))
        except FileNotFoundError:
            return JsonResponse({"error": f"File not found: {full_path}"}, status=404)

        context = {
            'packaging_density': packd_list,
            'vol_occ_curr': vol_curr_list,
            'vol_container':vol_container_list,
            'container_type' : container_type,
            'container_indices' : list(container_indices),
            'threed_paths': threed_data,
            'container_inf' : containerList,
            'num_skus': list(range(1, len(df) + 1)),
            'colors' : distinct_colors,
            'sku_info':[
            [int(sku[0]), float(sku[1]), float(sku[2]), float(sku[3]), float(sku[4])] 
            for sku in sku_info
        ],
            'box_info':[
            [float(info) for info in box] 
            for box in box_info
        ],
            'df':df_ht
        }
        # print(num_placed)
        # return render(request, 'freeOutput.html', context)  # Redirect to a success page
        return JsonResponse(context, safe=False)  # Redirect to a success page
    # return render(request, 'freeOutput.html')
    return JsonResponse({"error": "Invalid request"}, status=400)

def check_email(request):
    email_id = request.POST.get('email')
    user_exists = Users.objects.filter(email_id=email_id).exists()
    if user_exists:
        return JsonResponse({"ERROR": "User already exist try login"}, status=400)
    return JsonResponse({"SUCCESS": "Email is not register"}, status=400)


def send_otp_to_email(request):
    print(f"User email in view: {getattr(request, 'user_email', 'None')}")
    if hasattr(request, 'user_email'):
        return JsonResponse({'ERROR': f'Already logged in as {request.user_email}!'})
    # Step 1: Get the email from the request (assuming it's a POST request)
    email_id = request.POST.get('email')
    
    if not email_id:
        return JsonResponse({"ERROR": "Company Email is required"}, status=400)
    
    # Step 2: Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Step 3: Save OTP and email_id in the database
    otp_entry, created = OTPRegistration.objects.get_or_create(email_id=email_id)
    
    # If OTP entry exists, update the fields
    otp_entry.otp = otp
    otp_entry.isVerified = False
    otp_entry.otp_sent_time = timezone.now()
    otp_entry.expired = False
    otp_entry.save()

    # Step 4: Send the OTP via email
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. It is valid for 15 minutes.'
    email_from = DEFAULT_FROM_EMAIL
    recipient_list = [email_id]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        return JsonResponse({"SUCCESS": "OTP send successfully","sendTime":f"{otp_entry.otp_sent_time}"}, status=200)
    except Exception as e:
        return JsonResponse({"ERROR": f"Failed to send OTP. Error: {str(e)}"}, status=500)

def verify_otp(request):
    # Step 1: Get the email and otp from the request
    email_id = request.POST.get('email')
    otp_input = request.POST.get('otp')
    companyname = request.POST.get('company_name')
    
    if not email_id or not otp_input:
        return JsonResponse({"ERROR": "Email and OTP are required"}, status=400)
    
    try:
        # Step 2: Fetch the latest OTP entry for the given email
        otp_entry = OTPRegistration.objects.filter(email_id=email_id).latest('otp_sent_time')
        
        # Step 5: Check if the OTP is valid
        if otp_entry.otp != otp_input:
            return JsonResponse({"ERROR": "Invalid OTP"}, status=400)
        # Step 3: Check if the OTP has already been verified
        if otp_entry.isVerified:
            return JsonResponse({"ERROR": "OTP has already been verified"}, status=400)
        time_difference = timezone.now() - otp_entry.otp_sent_time
        # Step 4: Check if the OTP is expired
        if otp_entry.expired:
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        if time_difference > timedelta(minutes=15):
            # Mark the OTP as expired
            otp_entry.expired = True
            otp_entry.save()
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        # Step 6: Mark OTP as verified
        otp_entry.isVerified = True
        otp_entry.save()
        company, created = Company.objects.get_or_create(company_name=companyname)
    
        if created and not company.company_code:
            company.company_code = company.generate_unique_code()
            company.save()
        # Determine user type based on user count
        if company.user_count == 0:
            user_type = "Company_Admin"
        else:
            user_type = "None"
        user = Users(
            email_id=email_id,
            user_id=generate_unique_user_id(),
            user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
            user_last_name='DefaultLastName',    # Replace with actual form data or defaults
            user_type=user_type,
            user_status='Active',
            is_authenticated=True,
            company=company,
            first_login = timezone.now()
        )
        user.save()

        # Update the user count in the company
        company.user_count += 1
        company.save()
        token = generate_jwt_token(email_id,user.user_type,companyname)
        print(token)
        response = JsonResponse({"SUCCESS": {
                'email': email_id,
                'userType': user.user_type,
                "message" : "OTP verified successfully",
                "company" : user.company_id
            }}, status=200)
        response.set_cookie(
            'jwt_token',  
            token,        
            max_age=18000, 
            httponly=True, 
            secure=False,  
            samesite='Lax' 
        )
        if user.user_type != "Company_Admin":
            admin_user = Users.objects.filter(company=company, user_type="Company_Admin").first()
            if admin_user:
                send_mail(
                    subject="New User Registered in Your Company",
                    message=f"A new user with email {email_id} has registered with your company '{companyname}'.",
                    from_email=DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_user.email_id],  # Send to the company admin's email
                    fail_silently=False,
                )
        return response
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

def verify_login(request):
    # Step 1: Get the email and otp from the request
    email_id = request.POST.get('email')
    otp_input = request.POST.get('otp')
    company = request.POST.get("company_name")
    if not email_id or not otp_input:
        return JsonResponse({"ERROR": "Email and OTP are required"}, status=400)
    
    user_exists = Users.objects.filter(email_id=email_id).first()
    if not user_exists:
        return JsonResponse({"ERROR": "User not registered"}, status=400)
    try:
        # Step 2: Fetch the latest OTP entry for the given email
        otp_entry = OTPRegistration.objects.filter(email_id=email_id).latest('otp_sent_time')
        
        # Step 5: Check if the OTP is valid
        if otp_entry.otp != otp_input:
            return JsonResponse({"ERROR": "Invalid OTP"}, status=400)
        # Step 3: Check if the OTP has already been verified
        if otp_entry.isVerified:
            return JsonResponse({"ERROR": "OTP has already been verified"}, status=400)
        time_difference = timezone.now() - otp_entry.otp_sent_time
        # Step 4: Check if the OTP is expired
        if otp_entry.expired:
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        if time_difference > timedelta(minutes=15):
            # Mark the OTP as expired
            otp_entry.expired = True
            otp_entry.save()
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        # Step 6: Mark OTP as verified
        otp_entry.isVerified = True
        otp_entry.save()
        if user_exists:
            user_exists.last_login = timezone.now()
            user_exists.save()
            token = generate_jwt_token(email_id,user_exists.user_type,company)
            response = JsonResponse({"SUCCESS": {
                'email': email_id,
                'userType': user_exists.user_type,
                "message" : "OTP verified successfully",
                "company" : user_exists.company_id
            }}, status=200)
            response.set_cookie(
                'jwt_token',  
                token,        
                max_age=18000, 
                httponly=True, 
                secure=False,  
                samesite='Lax' 
            )
            return response
        else :
            return JsonResponse({"ERROR": "User not registered"}, status=400)
        
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

def check_login(request):
    if hasattr(request, 'user_email'):
        return JsonResponse({'SUCCESS': {
                'email': request.user_email,
                'userType': request.userType,
                'company' : request.company,
                "message" : "User is login"
            }})
    else:
        return JsonResponse({'Error': 'Unauthorized access, please log in'}, status=401)

def add_permission(request):
    if request.method == 'POST':
        if not hasattr(request,"userType") and not request.userType == "Company_Admin":
            return JsonResponse({"ERROR": "Login with admin account"}, status=400)
        try: 
            data = json.loads(request.body)  # Load JSON data from the request body
            company = ""
            for record in data:
                company_name = record.get('company')
                company = company_name
                user_type_name = record.get('user_type')
                dashboard_name = record.get('dashboard')
                allowed = record.get('allowed')

                # Step 1: Retrieve or create the related objects (Company, UserType, Dashboard)
                company = Company.objects.get(company_name=company_name)
                dashboard = Dashboard.objects.get(name=dashboard_name)
                user_type = UserType.objects.get(name=user_type_name)

                # Step 2: Check if a DashboardPermission record exists for this combination
                permission, created = DashboardPermission.objects.get_or_create(
                    company=company,
                    user_type=user_type,
                    dashboard=dashboard,
                    defaults={'allowed': allowed}
                )

                # Step 3: If it exists, update the 'allowed' field if it's different
                if not created:
                    if permission.allowed != allowed:
                        permission.allowed = allowed
                        permission.save()
            
            permissions = DashboardPermission.objects.filter(company=company)
            print("permissions")
            print(permissions)
            result = []
            for perm in permissions:
                print(perm)
                result.append({
                    "company": perm.company.company_name,
                    "user_type": perm.user_type.name,
                    "dashboard": perm.dashboard.name,
                    "allowed": perm.allowed
                })
            # print(result)

            return JsonResponse({"SUCCESS": result}, status=200)

        except Company.DoesNotExist:
            return JsonResponse({"ERROR": f"Company '{company_name}' does not exist"}, status=400)
        except UserType.DoesNotExist:
            return JsonResponse({"ERROR": f"User type '{user_type_name}' does not exist"}, status=400)
        except Dashboard.DoesNotExist:
            return JsonResponse({"ERROR": f"Dashboard '{dashboard_name}' does not exist"}, status=400)
        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)
    
    return JsonResponse({"ERROR": "Invalid request method"}, status=405)

def get_permissions(request):
    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            company = Company.objects.get(company_name=company_name)
            
            permissions = DashboardPermission.objects.filter(company=company)
            
            result = []
            for perm in permissions:
                result.append({
                    "company": perm.company.company_name,
                    "user_type": perm.user_type.name,  
                    "dashboard": perm.dashboard.name, 
                    "allowed": perm.allowed
                })
            
            return JsonResponse({"SUCCESS": result}, status=200)

        except Company.DoesNotExist:
            return JsonResponse({"ERROR": "Company not found"}, status=404)
    
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can view this data'}, status=403)
def add_loadplan(request):
    if request.method == 'POST':
        if hasattr(request, 'userType') and request.userType == "Company_Admin":
            company_name = request.company  
            
            try:
                company = Company.objects.get(company_name=company_name)
                data = json.loads(request.body)

                shipping_location = data.get("shipping_location", "")
                destination_location = data.get("destination_location", "")
                container_type = data.get("container_type", "")

                if shipping_location:
                    if shipping_location not in company.shipping_location:
                        company.shipping_location.append(shipping_location)  
                if destination_location:
                    if destination_location not in company.destination_location:
                        company.destination_location.append(destination_location)  
                if container_type:
                    if container_type not in company.container_type:
                        company.container_type.append(container_type)  

                company.save()

                result = {
                    "company": company.company_name,
                    "shipping_location": company.shipping_location,
                    "destination_location": company.destination_location,
                    "container_type": company.container_type,
                }

                return JsonResponse({"SUCCESS": result}, status=200)

            except Company.DoesNotExist:
                return JsonResponse({"ERROR": "Company not found"}, status=404)
        
        else:
            return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can add this data'}, status=403)

    else:
        return JsonResponse({'ERROR': 'Invalid request method. Only POST requests are allowed.'}, status=405)

def get_loadplan(request):
    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            company = Company.objects.get(company_name=company_name)
            result = {
                "company": company.company_name,
                "shipping_location": company.shipping_location, 
                "destination_location": company.destination_location,  
                "container_type": company.container_type,  
            }
            return JsonResponse({"SUCCESS": result}, status=200)

        except Company.DoesNotExist:
            return JsonResponse({"ERROR": "Company not found"}, status=404)
    
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can view this data'}, status=403)

def add_container(request):
    if request.method == 'POST':
        if hasattr(request, 'userType') and request.userType == "Company_Admin":
            company_name = request.company  
            
            try:
                company = Company.objects.get(company_name=company_name)
                
                data = json.loads(request.body)
                
                container_height = data.get('container_height')
                container_width = data.get('container_width')
                container_length = data.get('container_length')
                container_name = data.get('container_name')
                
                if not all([container_height, container_width, container_length, container_name]):
                    return JsonResponse({"ERROR": "Missing required fields"}, status=400)
                
                # Create a new container entry
                new_container = Container(
                    container_id=company.generate_unique_code(),
                    container_name=container_name,
                    container_height=container_height,
                    container_width=container_width,
                    container_length=container_length,
                    company=company  # Associate the container with the company
                )
                
                # Save the new container
                new_container.save()

                # Prepare the success response
                result = company.containers.values_list('container_name', flat=True)
                
                return JsonResponse({"SUCCESS": {
                'result': list(result),
                "message" : "Container added successfully"
            }}, status=201)
            
            except Company.DoesNotExist:
                return JsonResponse({"ERROR": "Company not found"}, status=404)
        
        else:
            return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can add containers'}, status=403)
    
    return JsonResponse({'ERROR': 'Invalid request method, use POST'}, status=405)

def get_container(request):

    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            company = Company.objects.get(company_name=company_name)
            result = company.containers.values_list('container_name', flat=True)
            
            return JsonResponse({"SUCCESS": list(result)}, status=200)

        except Company.DoesNotExist:
            return JsonResponse({"ERROR": "Company not found"}, status=404)
    
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can view this data'}, status=403)

def send_email(request):
    if request.method == 'POST':
        if hasattr(request, 'userType') and request.userType == "Company_Admin":
            company_name = request.company  
            
            try:
                data = json.loads(request.body)
                email_id = data.get("email")
                user_type = data.get("userType")
                user_exists = Users.objects.filter(email_id=email_id).exists()
                if not email_id or not user_type:
                    return JsonResponse({"ERROR": "Email and userType are required"}, status=400)
                if user_exists:
                    return JsonResponse({"ERROR":"User already exist"}, status=400)
                company = Company.objects.get(company_name=company_name)
                user = Users(
                    email_id=email_id,
                    user_id=generate_unique_user_id(),
                    user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
                    user_last_name='DefaultLastName',    # Replace with actual form data or defaults
                    user_type=user_type,
                    user_status='Dormant',
                    is_authenticated=True,
                    company=company,
                    first_login = timezone.now()
                )
                user.save()
                company.user_count += 1
                company.save()
                send_mail(
                    subject=f"Invited to join the '{company_name}'",
                    message=data.get("message"),
                    from_email=DEFAULT_FROM_EMAIL,
                    recipient_list=[data.get("email")],  # Send to the company admin's email
                    fail_silently=False,
                )
                return JsonResponse({"SUCCESS": "Email send successfully"}, status=201)
            except Company.DoesNotExist:
                return JsonResponse({"ERROR": "Company not found"}, status=404)
            except Exception as e:
                return JsonResponse({"ERROR": str(e)}, status=500)
        else:
            return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can add containers'}, status=403)
    return JsonResponse({'ERROR': 'Invalid request method, use POST'}, status=405)

def get_allusers(request):
    
    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            company = Company.objects.get(company_name=company_name)

            # Filter users based on the company
            users = Users.objects.filter(company=company)

            # Prepare the result
            user_data = []
            for user in users:
                user_data.append({
                    "user_id": user.user_id,
                    "email_id": user.email_id,
                    "user_first_name": user.user_first_name,
                    "user_last_name": user.user_last_name,
                    "user_type": user.user_type,
                    "user_status": user.user_status,
                    "first_login": user.first_login,
                    "last_login": user.last_login,
                    "is_active": user.is_active,
                    "is_authenticated": user.is_authenticated,
                })

            # Return the JSON response with the user data
            return JsonResponse({"SUCCESS": {
                "result": user_data,
                "message":"User fetched successfully"
            }}, status=200)

        except Exception as e:
                return JsonResponse({"ERROR": str(e)}, status=500)
    
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can view this data'}, status=403)

def get_usertype(request):

    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            user_types = UserType.objects.values_list('name', flat=True)
            user_type_list = list(user_types)  

            return JsonResponse({"SUCCESS": {
                "result":user_type_list,
                "message":"User type fetch successfully"
            }}, status=200)


        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)
    
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can view this data'}, status=403)

def update_usertype(request):

    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            data = json.loads(request.body)
            email_id = data.get("email")
            user_type = data.get("userType")

            if not email_id or not user_type:
                return JsonResponse({"ERROR": "Email and userType are required"}, status=400)

            user = Users.objects.filter(email_id=email_id, company=company_name).first()

            if not user:
                return JsonResponse({"ERROR": "User not found in the company"}, status=404)

            # Update the user type
            user.user_type = user_type
            user.save()

            return JsonResponse({"SUCCESS": {
                "message":"Role updated successfully"
            }}, status=200)

        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)

    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can update user type'}, status=403)

def remove_user(request):
    if hasattr(request, 'userType') and request.userType == "Company_Admin":
        company_name = request.company
        try:
            data = json.loads(request.body)
            email_id = data.get("email")

            if not email_id:
                return JsonResponse({"ERROR": "Email are required"}, status=400)
            user = Users.objects.filter(email_id=email_id, company=company_name).first()

            if not user:
                return JsonResponse({"ERROR": "User not found in the company"}, status=404)
            company = user.company
            user.delete()
            if company.user_count > 0:
                company.user_count -= 1
                company.save()

            return JsonResponse({"SUCCESS": {"message" : "User deleted successfully"}}, status=200)
        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)
    else:
        return JsonResponse({'ERROR': 'Unauthorized access, only Company_Admin can remove users'}, status=403)

# def add_sku(request):
#     if hasattr(request, 'userType') and request.userType == "Company_Admin":
#         company_name = request.company
#         try:
#             data = json.loads(request.body)     
#             # add sku data
            