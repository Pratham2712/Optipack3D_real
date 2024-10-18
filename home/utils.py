import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import pandas as pd
import json
import time
from copy import deepcopy
from itertools import permutations
import os
import heapq
import bisect


# app = Flask(__name__)

storage_boxes=pd.DataFrame()
storage_truck_spec={}
max_memory_usage = 0  # Initialize max memory usage


# @app.route('/dataProcess')
# def data_process():
#     return render_template('dataProcess.html')

def hex_to_0x(hex_code):
    if hex_code.startswith('#'):
        hex_code = hex_code[1:]
    int_value = int(hex_code, 16)
    return f"0x{int_value:06X}"

# @app.route('/upload_excel', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify(success=False), 400
    
#     specified_columns = ['Weight', 'Height', 'Volume']
#     units = {
#         'Weight': ['Pounds', 'Kgs', 'Tonnes'],
#         'Height': ['Meters', 'Inches', 'Feet'],
#         'Volume': ['Liters', 'Gallons', 'Cubic meters']
#     }

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify(success=False), 400

#     if file and (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
#         df = pd.read_excel(file)
#         columns = df.columns.tolist()
#         return jsonify(success=True, columns=columns, specified_columns=specified_columns, units=units)

#     return jsonify(success=False), 400


# @app.route('/mapping',methods=['POST','GET'])
# def mapping():
#     with open('static/matched_columns.json', 'r') as f:
#         matched_columns = json.load(f)
#     # print("mapping",matched_columns)
#     return render_template('mapping.html', matched_columns=matched_columns)
# @app.route('/match_columns', methods=['POST'])
# def match_columns():
#     matched_columns = request.json
#     # Process the matched columns here
#     # print(matched_columns)

#     with open('static/matched_columns.json', 'w') as f:
#         json.dump(matched_columns, f)
#     return jsonify(success=True)




# Truck specifications nested dictionary used to retrieve truck dimensions 
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


#Used to process the submitted data (in .xlsx or .csv format) to required format such that it can be passesd to different functions and also updated.
# I have converted it to pandas dataframes 
def DataProcess(df, truck_spec, perc, dataP, data):
    # Extract container dimensions and max weight from truck specifications
    length_container = truck_spec['length_container']
    width_container = truck_spec['width_container']
    height_container = perc * truck_spec['height_container']
    max_weight = truck_spec['max_weight']
    # print(data)
    # print(df)
    # List of columns in the input data
    col_list = data.columns.tolist()

    # Accessing columns using bracket notation based on the value of dataP
    if dataP == 2:
        # Extracting data when dataP equals 2
        length = df['Length']
        width = df['Width']
        height = df['Height']
        numOfcases = df['TotalCases']
        rotation_allowed = df['Alpha(rotation about Z-axis)']
        gross_weight = df['GrossWeight']
        net_weight = data[col_list[1]].tolist()
        temperature = data[col_list[3]].tolist()
        vol = data[col_list[2]].tolist()
        colors = data[col_list[len(col_list)-1]].tolist()

    else:
        # Extracting data when dataP is not equal to 2
        gross_weight = data[col_list[0]].tolist()
        net_weight = data[col_list[1]].tolist()
        vol = data[col_list[2]].tolist()
        height = data[col_list[6]].tolist()
        numOfcases = data[col_list[7]].tolist()
        rotation_allowed = data[col_list[8]].tolist()
        temperature = data[col_list[3]].tolist()
        length = data[col_list[4]].tolist()
        width = data[col_list[5]].tolist()
        colors = data[col_list[len(col_list)-1]].tolist()

    # Define the Product class to represent individual products
    class Product:
        def __init__(self, length, width, height, grossWeight, netWeight, temperature, volume, numberOfCases):
            self.length = length
            self.width = width
            self.height = height
            self.grossWeight = grossWeight
            self.netWeight = netWeight
            self.temperature = temperature
            self.volume = volume
            self.numberOfCases = numberOfCases

    # Define the Container class to represent the container
    class Container:
        def __init__(self, length, width, height, max_weight, front_axle_weight, rear_axle_weight, front_axle_distance, rear_axle_distance):
            self.length = length
            self.width = width
            self.height = height
            self.max_weight = max_weight
            self.front_axle_weight = front_axle_weight
            self.rear_axle_weight = rear_axle_weight
            self.front_axle_distance = front_axle_distance
            self.rear_axle_distance = rear_axle_distance

    # Function to create a strip list for fitting boxes into the container
    def create_strip_list(box, container):
        box_len = float(box.length)
        box_width = float(box.width)
        box_height = float(box.height)

        container_len = float(container.length)
        container_width = float(container.width)
        container_height = height_container

        if box_len < container_len and box_width < container_width:
            num_of_boxes_fit = container_height // box_height
            return [box_len, box_width, box_height, num_of_boxes_fit]
        else:
            return []

    # Axle weights and distances for the container
    front_axle_weight = 16000
    rear_axle_weight = 12400
    front_axle_dist = 2890
    rear_axle_dist = 3000

    # Create a container object with the specified dimensions and weights
    container_toFit = Container(length_container, width_container, height_container / perc, max_weight, front_axle_weight, rear_axle_weight, front_axle_dist, rear_axle_dist)

    # Initialize a list to store products
    num_typesOfBoxes = len(gross_weight)
    box_set = []

    # Create Product objects and add them to the box_set list
    for i in range(num_typesOfBoxes):
        box = Product(length[i], width[i], height[i], gross_weight[i], net_weight[i], temperature[i], vol[i], numOfcases[i])
        box_set.append(box)
                                    
    # Create a list of strips for each product
    strip_list = []
    for box in box_set:
        strips = create_strip_list(box, container_toFit)
        strip_list.append(strips)

    # Function to calculate remaining boxes and number of strips per box type
    def remBoxes(box_set, strip_list):
        rem_boxes = []
        num_of_strips_per_boxType = []
        i = 0
        for box in box_set:
            num = int(box.numberOfCases)
            num_per_strip = strip_list[i][3]
            num_of_strips = num // num_per_strip
            rem = num % num_per_strip
            num_of_strips_per_boxType.append(num_of_strips)
            rem_boxes.append(rem)
            i += 1
        return rem_boxes, num_of_strips_per_boxType

    # Calculate remaining boxes and number of strips per box type
    rem_boxes, num_strips_box = remBoxes(box_set, strip_list)

    # Append additional information to the strip list
    for i in range(len(strip_list)):
        strip_list[i].append(num_strips_box[i])
        strip_list[i].append(rem_boxes[i])
        strip_list[i].append(int(box_set[i].numberOfCases))  # Indicating that it has been used
        strip_list[i].append(True)
        strip_list[i].append(rotation_allowed[i])
        strip_list[i].append(float(box_set[i].grossWeight))

    # Convert strip list elements to float
    for i in range(len(strip_list)):
        for j in range(len(strip_list[i])):
            strip_list[i][j] = float(strip_list[i][j])

    # If dataP equals 2, process and return the dataframe with additional columns (if df was used earlier, update any changes to the new one and pass)
    if dataP == 2:
        df_new = pd.DataFrame(strip_list)
        df_new.columns = ['Length', 'Width', 'Height', 'NumOfBoxesPerStrip', 'TotalNumStrips', 'Rem_Boxes', 'TotalCases', 'Marked', 'Alpha(rotation about Z-axis)', 'GrossWeight']

        # Add 'BoxNumber' column
        df_new['BoxNumber'] = df_new.index

        # Define color dictionary
        colors = {i: color for i, color in enumerate(colors)}

        # Add 'Color' column
        df_new['Color'] = df_new['BoxNumber'].map(colors)
        df_new = df_new[['BoxNumber', 'Color'] + [col for col in df_new.columns if col not in ['BoxNumber', 'Color']]]
        df_new['Rem_Strips'] = df['Rem_Strips']
        df_new['Rem_Boxes'] = df['Rem_Boxes']

        return df_new, container_toFit, strip_list

    # If dataP equals 1, process and return the dataframe with additional columns (This is when new data has just come and has not filled any container)
    elif dataP == 1:
        df = pd.DataFrame(strip_list)
        df.columns = ['Length', 'Width', 'Height', 'NumOfBoxesPerStrip', 'TotalNumStrips', 'Rem_Boxes', 'TotalCases', 'Marked', 'Alpha(rotation about Z-axis)', 'GrossWeight']

        # Add 'BoxNumber' column
        df['BoxNumber'] = df.index

        # Define color dictionary
        colors = {i: color for i, color in enumerate(colors)}
        
        # Add 'Color' column
        df['Color'] = df['BoxNumber'].map(colors)
        df = df[['BoxNumber', 'Color'] + [col for col in df.columns if col not in ['BoxNumber', 'Color']]]
        df['Rem_Strips'] = df['TotalNumStrips']

        return df, container_toFit, strip_list
    
    # If dataP is neither 1 nor 2, print an error message and return -1
    else:
        print("Please put correct DataProcess Number!")
        return -1



# Used to place the boxes in a strip with height constraint 
def placeStrips(box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row):

    #Used to retrieve the number of boxes in strip from striplist
    num_boxes_in_a_strip = strip_list[box_num][3]


    #Used to store strip for further calculations 
    storage_strip.append([y,strip_list[box_num][3] * strip_list[box_num][9]])
    while num_boxes_in_a_strip > 0 and curr_weight+box_weight < max_weight:
        ax.bar3d(x, y, z, box_width, box_length, box_height, color=color, edgecolor='black')
        box_storer.append({"start": {"x": x, "y": y, "z": z}, "end": {"x": x, "y": y, "z": z+box_height}, "color":hex_to_0x(color),
                            "dimensions":{"length":box_length,"width":box_width,"height":box_height},"row":row})
        z += box_height
        num_boxes_in_a_strip -= 1
        curr_weight+=strip_list[box_num][9]
        vol_occ+=box_length*box_width*box_height
    
    return box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row


#Checks which one is more filling and keeps less space after placing in a row. (Row-wise)
def invertOrNot(x,end_x,box_num,box_length,box_width,box_height,width_container,total_strips):
    rem_width= end_x-x
    if rem_width <=0:
        return False
    num_strips_required = rem_width//box_width
    if num_strips_required > total_strips:
        return False
    perc_nonInverted = ((rem_width//box_width)*box_width)/rem_width
    perc_Inverted = ((rem_width//box_length)*box_length)/rem_width


    if perc_Inverted > perc_nonInverted:
        return True

    else:
        return False
        

#Uses the previous row data to find the optimum y (to place the next row) in order to minimize the space (Used heap to decrease the time complexity)
def findoptlen(prev_row,x,y,end_x,box_width,row,prev_y,prev_row_num,container_toFit):
# Filter out invalid prev_row entries
    valid_prev_row = [(item[6], i, item) for i, item in enumerate(prev_row) if item[0] != item[2]]
    
    # Create a min-heap based on row numbers
    heapq.heapify(valid_prev_row)
    # print("Heap elements:", list(valid_prev_row))  

    # Find the smallest valid row number
    while valid_prev_row:
        current_row_num, idx, current_item = heapq.heappop(valid_prev_row)
        if row - 1 <= current_row_num <= row:
            break
    else:
        # If no valid entry is found, return the original values
        return y, end_x, row, prev_row, prev_y, prev_row_num

    # Check if end_x + box_width exceeds container width and adjust if necessary
    if end_x + box_width > float(container_toFit.width) and len(prev_row) <= 1:
        end_x = float(container_toFit.width)
    else:
        end_x = deepcopy(current_item[2])

    y = current_item[3]
    prev_row_num = deepcopy(current_item[6])
    prev_y = deepcopy(current_item[1])
    current_item[5] = 0
    prev_row.pop(idx)

    return y, end_x, row, prev_row, prev_y, prev_row_num






#Main box placing algorithm.

def box_placer(total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,container_toFit,row,prev_y,color,allowed,box_storer):

    while total_strips > 0 and y > 0 and curr_weight+box_weight<max_weight:
        if x + box_width <= end_x and x + box_width <= width_container:  ## added the max weight check constraints
         
            if len(prev_row) >1 and prev_row[len(prev_row)-2][1]>=0 and y-prev_row[len(prev_row)-2][1] > box_length and row== prev_row[len(prev_row)-2][6]:
                
                box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row =placeStrips(box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row)

          
                z = 0
                total_strips -= 1
                
                if total_strips==0:
                    x+=box_width
                    continue
                if total_strips>0:
                    if y-box_length>=0:
                        y-=box_length
                    else:
                        continue
                    prev_row[len(prev_row)-1][1]=deepcopy(y)
                    
                    
                    box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row =placeStrips(box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row)

                    
                    x+=box_width

                    if x+box_width<=end_x:
                        y+=box_length
                    z=0
                   

                    total_strips-=1

             


            else:
                box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row =placeStrips(box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row)
                
           
                x += box_width
                z = 0
                total_strips -= 1

            

        else: 
           
            y_min = min(y_min,y)
            if x+box_width> width_container:
              
                vol_wasted += abs(width_container-x)*box_length*height_container

                x = width_container
            

            prev_row[len(prev_row)-1].append(x)
            prev_row[len(prev_row)-1].append(y)
            prev_row[len(prev_row)-1].append(box_length)
            prev_row[len(prev_row)-1].append(1)
            prev_row[len(prev_row)-1].append(row)
            
            # index=0
            if x + box_width > width_container:
                
                row+=1
                x = 0
                z = 0
            
            # index=0
            keys = [item[6] for item in prev_row]

            # Define a function to find the first index of the target using binary search
            def find_first_index(keys, target):
                index = bisect.bisect_left(keys, target)
                # Check if the target is actually present at the found index
                if index < len(keys) and keys[index] == target:
                    return index
                return -1

            # Now use the function to find the first index of the desired row number
            target = row - 1
            index = find_first_index(keys, target)
            # while index<len(prev_row) and (prev_row[index][6]!=row-1):
            #     index+=1

          
            rem=0
            rem_y=0
            went_in_1 = False
            went_in_2 =False
            if x!=0 and end_x-x< (x+box_width)-end_x: 
                ##Checks the better one between putting one extra or shifting according to the previous row
                
                rem=deepcopy(abs(x-end_x))
                if len(prev_row) >1 and index<len(prev_row) and prev_row[index][6] == prev_row_num and prev_row[index][3] > prev_y:
                    went_in_1=True
                x +=(end_x-x)
            else:
                if len(prev_row) >1 and index<len(prev_row) and prev_row[index][6] == prev_row_num and prev_row[index][3] > prev_y and x + box_width <= width_container:
                    went_in_2=True
                  
                    box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row =placeStrips(box_num,storage_strip,strip_list,ax,z,box_height,curr_weight,vol_occ,box_length,box_width,max_weight,color,box_weight,x,y,box_storer,row)
                    x += box_width
                    z = 0
                    total_strips -= 1
                    prev_row[len(prev_row)-1][2]=deepcopy(x)
                    rem=deepcopy(abs(x-end_x))
                 


            p_y=0
            if went_in_1 is True:
                p_y = deepcopy(y+box_length)
            elif went_in_1 is False and went_in_2 is False:
                p_y = deepcopy(box_length)
            else:
                p_y = deepcopy(y+box_length)




            y,end_x,row,prev_row,prev_y,prev_row_num= (findoptlen(prev_row,x,y,end_x,box_width,row,prev_y,prev_row_num,container_toFit))

            if x!=0 and went_in_1 is True:
          
                vol_wasted += abs(y-box_length-p_y)*rem*height_container
            elif x!=0 and went_in_1 is False and went_in_2 is False:
                vol_wasted += abs(p_y)*rem*height_container
            else:
                if x!=0:
                    vol_wasted += abs(y-p_y)*rem*height_container
            y_min = min(y_min,y)

        
            if end_x+box_width>=width_container:  
                end_x = deepcopy(width_container)
            
            change = invertOrNot(x,end_x,box_num,box_length,box_width,box_height,width_container,total_strips)
    

            if change == True and allowed:
                temp = deepcopy(box_length)
                box_length = deepcopy(box_width)
                box_width = deepcopy(temp)


            y = y -1-box_length
            y_min = min(y_min,y)

            prev_row.append([x,y])

    return total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,row,prev_y,color,box_storer
    

#Used to create the base ax plot on which the boxes will be placed. (3D)
def create_plot(container):
    width_container = float(container.width)
    height_container = float(container.height)
    length_container = float(container.length)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(0, width_container)
    ax.set_ylim(0, length_container)
    ax.set_zlim(0, height_container)

    # Set labels for axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_box_aspect([1, length_container/width_container, height_container/width_container])


    # Dont show the plot
    plt.ioff()
    return ax


#Stability Function defined below. 80% contribution from vol_wasted, 10% to vol_occupied and withOrder and WeightDistribution 5% each
def stability(weight_leftHalf, weight_rightHalf,best_widht_order,curr_width_order,vol_wasted,vol_occupied):
    # Finding the percentage difference betweeenn the load on the front and rear axel from the centre line 
    front_axel_perc = weight_leftHalf/(weight_rightHalf+weight_leftHalf+0.01)
    penalty_weight = 0
    penalty_width_order = 0
    if front_axel_perc>0.6 :
        penalty_weight = abs(front_axel_perc-0.6)*10
    elif front_axel_perc<0.5:
        penalty_weight = abs(front_axel_perc-0.5)*10

    for i in range(len(curr_width_order)):
        if best_widht_order[i]==curr_width_order[i]:
            penalty_width_order+=1
        else:
            penalty_width_order-=1
            
    stab = round(0.8*vol_wasted-( 0.1*vol_occupied/100)-0.05*penalty_width_order-0.05*penalty_weight,2)

    return stab


#Calculating weight distribution
def weight_distribution(container_toFit,storage_strip):
    weight_sum_lower_half = 0
    weight_sum_upper_half = 0

    threshold = container_toFit.length / 2

    for item in storage_strip:
        y, weight = item
        if y < threshold:
            weight_sum_lower_half += weight
        else:
            weight_sum_upper_half += weight

    return weight_sum_lower_half,weight_sum_upper_half

#Generating Ideal Width Order (Decreasing width)
def widthOrder(strip_list):
    temp = []
    for details in strip_list:
        temp.append(details[1])
    temp.sort(reverse=True)

    return temp

#Generating Colors 
def generate_colors(n):
    distinct_colors = ['red', 'blue', 'yellow', 'orange', 'green', 'violet', 'white', 'indigo', 'cyan', 'magenta', 'lime', 'pink', 'teal', 'lavender', 'brown', 'gray', 'black']

    if n <= len(distinct_colors):
        return {i: distinct_colors[i] for i in range(n)}
    else:
        new_colors = {}
        for i in range(n):
            new_colors[i] = distinct_colors[i % len(distinct_colors)]
        return new_colors
    

#Placing non homogenous strips
def place_nonH(x,y,z,colors,nH_list,container,ax,curr_weight,stored_plac,vol_occ,y_min,df,vol_wasted,storage_strip,box_storer,row): # Used for placing the non homogenous boxes
    width_container = float(container.width)
    height_container = float(container.height)
    depth_container = float(container.length)
    max_weight = float(container.max_weight)


    init_x=x
    init_y=y
    init_z=z

    total_boxes= 0
    max_len = 0
    max_width= 0

    for num in nH_list:
        total_boxes+= num[3]
        max_len = max(max_len,num[0])
        max_width = max(max_width,num[1])

    index = 0
    while total_boxes>0 and y > 0 and curr_weight + nH_list[index][5]<max_weight:

        while z<height_container and index < len(nH_list):
            rem_boxes = nH_list[index][3]
            box_num = nH_list[index][4]
            box_length = nH_list[index][0]
            box_width = nH_list[index][1]
            box_height = nH_list[index][2]
            box_weight = nH_list[index][5]
            

            temp = rem_boxes
            dw = False
            while temp>0 and z<height_container:
                if(x+box_width < width_container and curr_weight+box_weight < max_weight and z+box_height < height_container):
                    ax.bar3d(x, y, z, box_width, box_length, box_height, color=colors[box_num], edgecolor='black')
                    box_storer.append({"start": {"x": x, "y": y, "z": z}, "end": {"x": x, "y": y, "z": z+box_height}, "color":hex_to_0x(colors[box_num]),
                            "dimensions":{"length":box_length,"width":box_width,"height":box_height},"row":row})
                    z += box_height
                    temp -= 1
                    curr_weight+=nH_list[index][5]
                else:
                    dw = True
                    break
            
            nH_list[index][3] = temp
            df.at[box_num,'Rem_Boxes'] = temp
            total_boxes-=(rem_boxes-temp)
            if(dw==False and nH_list[index][3]==0):
                index+=1
            if dw == True and nH_list[index][3]!=0:
                x = x+max_width
                z=0


            if(x+max_width > width_container):
                x=0
                y = y-max_len
                z=0
 

        if z >height_container:
            if(x+max_width> width_container):
                x=0
                y = y-max_len
                z=0
            else:
                x= x+ max_width
                z = 0


    return  x,y,z,vol_occ,y_min,df,vol_wasted,storage_strip,nH_list,box_storer,row  ## Remember to add vol_occ calculation in the nonHomo 

def widthRem(width_rem,strip_list):
    for box in strip_list:

        if box[1] <= width_rem:
            return True
    
    return False


#Choosing the best dimensions amongst the top 2, sorted on least width rem > length_difference > width 
def choose_best_dimension(x,end_x,z,strip_list,container,stored_plac,df):

    width_container = float(container.width)
    height_container = float(container.height)
    depth_container = float(container.length)

    if end_x ==0:
        end_x = width_container

    width_rem = end_x-x

    checker = widthRem(width_rem,strip_list)
    if checker == False:
        width_rem = width_container

    
    index = 0
    best_width = []
    for box_dim in strip_list:
        if(box_dim[7]==0 and df.at[index,'Rem_Strips']==0):
            index+=1
            continue
        length_diff = 1e4
        num_box = width_rem//box_dim[1]
        total_num_strips = box_dim[4]
        height = box_dim[2]
        fill = True
        if num_box > total_num_strips:
            fill= False
        perc = (num_box*box_dim[1]/width_rem)
        if len(stored_plac)>0:
            prev_length = stored_plac[len(stored_plac)-1][7]
            length_diff = abs(box_dim[0]-prev_length)
        best_width.append([index,perc,box_dim[1],fill,length_diff,((height_container//height)*height)])
        index+=1

    sorted_data = sorted(best_width, key=lambda x: (x[3], x[1], x[5],x[2]), reverse=True)
    n =1    #Currently taking the best amongst top 2 only based on the efficiency.
    ind =0
    maxi =1e5
    best_box =-1
    while ind < len(sorted_data) and ind <= n :
        if maxi > sorted_data[ind][4] and sorted_data[ind][3]:
            maxi = min(maxi,sorted_data[ind][4])
            best_box = sorted_data[ind][0]
        ind+=1
    if best_box==-1 and len(sorted_data)>1:
        best_box = sorted_data[0][0]

    return best_box


#Placing Boxes in Heuristic Solution

def perform_computation(df,container_toFit,strip_list,key,roll):

    def after_plac(x,y,z,end_x,box_num,strip_list,container,ax,color,curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,df,vol_wasted,box_storer):
        width_container = float(container.width)
        height_container = float(container.height)
        depth_container = float(container.length)
        max_weight = container.max_weight


        init_x=x
        init_y=y
        init_z=z

        total_strips = deepcopy(df.at[box_num,'Rem_Strips'])
        box_length = deepcopy(float(strip_list[box_num][0]))
        box_width = deepcopy(float(strip_list[box_num][1]))
        box_height = deepcopy(float(strip_list[box_num][2]))
        box_weight = deepcopy(float(strip_list[box_num][9]))

        change_init = invertOrNot(x,end_x,box_num,box_length,box_width,box_height,width_container,total_strips)
        if change_init == True:
            
            y = y+box_length
            temp = deepcopy(box_length)
            box_length = deepcopy(box_width)
            box_width = deepcopy(temp)
            prev_row[len(prev_row)-1][1] = prev_row[len(prev_row)-1][1] + box_width- box_length
            y = y-box_length
        total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,row,prev_y,color,box_storer =box_placer(total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,container,row,prev_y,color,1,box_storer)


        
        if y<0 and total_strips!=0 and curr_weight+box_weight<max_weight:
            y+=box_length
            y-=box_width
            if y>0:
                temp = deepcopy(box_length)
                box_length = deepcopy(box_width)
                box_width = deepcopy(temp)
                total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,row,prev_y,color,box_storer =box_placer(total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,container,row,prev_y,color,0,box_storer)
            

        prev_row[len(prev_row)-1].append(x)
        prev_row[len(prev_row)-1].append(y)
        prev_row[len(prev_row)-1].append(box_length)
        prev_row[len(prev_row)-1].append(1)
        prev_row[len(prev_row)-1].append(row)
        y_min = min(y_min,y)
        df.at[box_num, 'Rem_Strips'] =total_strips
        df.at[box_num,'Marked'] = 0
        return x, y, z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,df,vol_wasted,storage_strip,curr_weight,box_storer
    
    
    #Creating the bottom view snapshot of the 3d plot
    def create_bottom_view(ax, vol_occ, vol_wasted, key, roll, stability_fin, packaging_density):
    # Adjust the viewing angle for bottom view
        ax.view_init(elev=90, azim=180)
        key = key.replace("'", "")

        # Create text annotation including vol_occ, vol_wasted, and packaging_density
        text_top = (f'vol_occ: {vol_occ:.2f}%\n'
                    f'vol_wasted: {vol_wasted:.2f}%\n'
                    f'{key}, roll: {roll}\n'
                    f'packaging_density: {packaging_density:.2f}')
        
        ax.text2D(0.05, 0.95, text_top, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        
        # Create text annotation for stability_fin at the bottom
        text_bottom = f'stability_fin: {stability_fin}'
        ax.text2D(0.05, 0.05, text_bottom, transform=ax.transAxes, fontsize=12,
                verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        
        # Save the plot as an image with a fixed filename
        filename = os.path.join('home/static/files/', f"{key}_roll{roll}_bottom_view.png")
        plt.savefig(filename)

        # Close the plot to free up resources
        plt.close()

        return filename  # Return the filename for reference


    #finding number of different SKUs
    n = len(strip_list)
   

    colors = df['Color'].tolist()
    # converted_colors = [hex_to_0x(color) for color in colors]

    # print(df)


    #Creating the required lists and variables for data handling 
    stored_plac = []
    box_storer=[]
    storage_strip=[]
    prev_row= []
    curr_width_order = []
    end_x = float(container_toFit.width)
    curr_weight = 0
    prev_y =-1
    y_min = 1e5
    row =0
    vol_occ = 0
    vol_wasted=0
    prev_row_num=-1

    #Creating Plot
    ax = create_plot(container_toFit)
    x,y,z= 0,0,0
    
    for i in range(len(strip_list)):
        if len(prev_row)==0 or len(prev_row)==1:
            end_x = float(container_toFit.width)
    
        ans =choose_best_dimension(x,end_x,z,strip_list,container_toFit,stored_plac,df)
        if ans==-1:
            break
        curr_width_order.append(strip_list[ans][1])
        strip_list[ans][7] = False
        if i == 0:
            y=container_toFit.length-strip_list[ans][0]-1
            y_min = min(y_min,y)
        if y<=0 or curr_weight+strip_list[ans][9]>container_toFit.max_weight:
            break
        if(i!=0 and row!=0):
            y = y-1+prev_row[len(prev_row)-1][4]-strip_list[ans][0]
            y_min = min(y_min,y)
            prev_row.append([x,y])
            x,y,z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,df,vol_wasted,storage_strip,curr_weight,box_storer= after_plac(x,y,z,end_x,ans,strip_list,container_toFit,ax,colors[ans],curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,df,vol_wasted,box_storer)
        else:
            if(i!=0 and row==0):
                y = y-1+prev_row[len(prev_row)-1][4]-strip_list[ans][0]
            prev_row.append([x,y])
            x,y,z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,df,vol_wasted,storage_strip,curr_weight,box_storer= after_plac(x,y,z,end_x,ans,strip_list,container_toFit,ax,colors[ans],curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,df,vol_wasted,box_storer)
    

    #Non homo placement
    nH_list =  []
    # print(df.at[i,'Rem_Boxes'])

    for i in range(len(df)):
        nH_list.append([df.at[i,'Length'],df.at[i,'Width'],df.at[i,'Height'],df.at[i,'Rem_Boxes'],i,df.at[i,'GrossWeight']])
    x,y,z,vol_occ,y_min,df,vol_wasted,storage_strip,nH_list,box_storer,row = place_nonH(x,y,z,colors,nH_list,container_toFit,ax,curr_weight,stored_plac,vol_occ,y_min,df,vol_wasted,storage_strip,box_storer,row)
    if y_min <0:
        y_min = 0


    #Collecting all the required informations for displaying (KPIs)
    packaging_density = (vol_occ/(container_toFit.width*container_toFit.height*(container_toFit.length-y_min)))
    vol_occ_curr =round(vol_occ/(container_toFit.length*container_toFit.width*container_toFit.height),2)*100
    # vol_wasted=
    vol_container= container_toFit.length*container_toFit.width*container_toFit.height
    perc_wasted = round(float(vol_wasted/(vol_container))*100,2)
    weight_leftHalf, weight_rightHalf = weight_distribution(container_toFit,storage_strip)
    best_width_order = widthOrder(strip_list)
    stability_fin = stability(weight_leftHalf,weight_rightHalf,best_width_order,curr_width_order,round(vol_wasted*pow(10,-9),2),vol_occ_curr)
    filename_final = create_bottom_view(ax,vol_occ_curr,perc_wasted,key,roll,stability_fin,packaging_density)
    # print(box_storer)
    if len(box_storer)!=0:
        box_storer.append({"last_box_y":container_toFit.length-y_min})
        
    box_coords_filename = f'home/static/files/box_coordinates_{roll}_{key}.json'
    container_info_filename = f'home/static/files/container_info_{roll}_{key}.json'

    with open(box_coords_filename, 'w') as file:
        json.dump(box_storer, file)

    container_info = {
        "containerLength": container_toFit.length,
        "containerWidth": container_toFit.width,
        "containerHeight": container_toFit.height
    }

    with open(container_info_filename, 'w') as file:
        json.dump(container_info, file)

    # Returning the filename and dataframe to the frontend to display
    box_coords_filename = box_coords_filename.replace('home/static/', '')
    container_info_filename = container_info_filename.replace('home/static/', '')
 
    box_coords = box_coords_filename
    container_inf = container_info_filename
    return filename_final,df,packaging_density,vol_occ_curr,perc_wasted,vol_container, box_coords, container_inf


def worker(df, container_toFit,strip_list,keys,roll,container_num):

    length_container = container_toFit.length
    width_container = container_toFit.width
    height_container = container_toFit.height
    
    def after_plac(x,y,z,end_x,box_num,strip_list,container,ax,color,curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,df,vol_wasted,box_storer):
        width_container = float(container.width)
        height_container = float(container.height)
        depth_container = float(container.length)
        max_weight = container.max_weight


        init_x=x
        init_y=y
        init_z=z

        total_strips = deepcopy(df.at[box_num,'Rem_Strips'])
        box_length = deepcopy(float(strip_list[box_num][0]))
        box_width = deepcopy(float(strip_list[box_num][1]))
        box_height = deepcopy(float(strip_list[box_num][2]))
        box_weight = deepcopy(float(strip_list[box_num][9]))

        change_init = invertOrNot(x,end_x,box_num,box_length,box_width,box_height,width_container,total_strips)
        if change_init == True:
            
            y = y+box_length
            temp = deepcopy(box_length)
            box_length = deepcopy(box_width)
            box_width = deepcopy(temp)
            prev_row[len(prev_row)-1][1] = prev_row[len(prev_row)-1][1] + box_width- box_length
            y = y-box_length



        total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,row,prev_y,color,box_storer =box_placer(total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,container,row,prev_y,color,1,box_storer)

        if y<0 and total_strips!=0 and curr_weight+box_weight<max_weight:
            y+=box_length
            y-=box_width
            if y>0:
                temp = deepcopy(box_length)
                box_length = deepcopy(box_width)
                box_width = deepcopy(temp)
                total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,row,prev_y,color,box_storer =box_placer(total_strips,x,y,z,curr_weight,box_weight,box_length,box_width,box_height,max_weight,box_num,storage_strip,strip_list,ax,vol_occ,prev_row,end_x,width_container,y_min,vol_wasted,prev_row_num,height_container,container,row,prev_y,color,1,box_storer)

            

        prev_row[len(prev_row)-1].append(x)
        prev_row[len(prev_row)-1].append(y)
        prev_row[len(prev_row)-1].append(box_length)
        prev_row[len(prev_row)-1].append(1)
        prev_row[len(prev_row)-1].append(row)
        y_min = min(y_min,y)
        df.at[box_num, 'Rem_Strips'] =total_strips
        df.at[box_num,'Marked'] = 0
        
        return x, y, z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,df,total_strips,vol_wasted,storage_strip,curr_weight,box_storer
    

    def create_bottom_view(ax, iteration, vol_occ_curr, vol_wasted, keys, roll, stability_fin, container_num, packaging_density):
    # Adjust the viewing angle for bottom view
        ax.view_init(elev=90, azim=180)
        keys = keys.replace("'", "")
        
        # Create text annotation including iteration number, vol_occ_curr, vol_wasted, and packaging_density
        text = (f'Iteration: {iteration}\n'
                f'vol_occ_curr: {vol_occ_curr:.2f}%\n'
                f'vol_wasted: {vol_wasted:.2f}%\n'
                f'Keys: {keys}\n'
                f'Roll: {roll}\n')
        
        ax.text2D(0.05, 0.98, text, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        
        # Create text annotation for stability_fin at the bottom
        text_bottom = (f'stability_fin: {stability_fin}\n'
        f'Packaging Density: {packaging_density:.2f}')
        ax.text2D(0.05, 0.05, text_bottom, transform=ax.transAxes, fontsize=12,
                verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        
        # Construct the filename including the iteration number, keys, and roll
        filename = os.path.join('home/static/files', f"bottom_view_iteration_final_{container_num}.png")
        plt.savefig(filename)
        
        # Close the plot to free up resources
        plt.close()

        return filename
    # Return the filename for reference


    
    n = len(strip_list)
    colors = generate_colors(n)

    
    def generate_permutations(n):
        numbers = list(range(n))
        perms = list(permutations(numbers))
        return perms

    n = len(strip_list)
    perms = generate_permutations(n)
    perms = list(perms)

    df_stored=[]
    best_width_order = widthOrder(strip_list)
    min_stab= 1e5
    final_df=-1
    final_filename = 'none'


    for i in range(len(perms)):
        print(perms[i])
        curr_order =[]
        tmp= deepcopy(df)
        vol_wasted=0
        stored_plac = []
        storage_strip=[]
        box_storer=[]
        vol_occ = 0
        ax = create_plot(container_toFit)
        y_min = 1e5
        prev_row= []
        end_x = float(container_toFit.width)
        curr_weight = 0
        prev_y =-1
        row =0
        prev_row_num=-1
        #Creating Plot
        x,z= 0,0
        for j in range(len(perms[i])):
            curr_order.append(strip_list[perms[i][j]][1])

            if len(prev_row)==0 or len(prev_row)==1:
                end_x = float(container_toFit.width)
        
            if j == 0:
                y=deepcopy(length_container-strip_list[perms[i][j]][0]-1)
                y_min = min(y_min,y)
            
            if y<0:
                break

            
            if(j!=0 and row!=0):
                y = y-1+prev_row[len(prev_row)-1][4]-strip_list[perms[i][j]][0]
                y_min = min(y_min,y)
                prev_row.append([x,y])
                x,y,z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,tmp,total_strips,vol_wasted,storage_strip,curr_weight,box_storer= after_plac(x,y,z,end_x,perms[i][j],strip_list,container_toFit,ax,colors[perms[i][j]],curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,tmp,vol_wasted,box_storer)
            else:
                if(j!=0 and row==0):
                    y = y-1+prev_row[len(prev_row)-1][4]-strip_list[perms[i][j]][0]
                y_min = min(y_min,y)
                prev_row.append([x,y])
                x,y,z,row,prev_y,prev_row,end_x,prev_row_num,vol_occ,y_min,tmp,total_strips,vol_wasted,storage_strip,curr_weight,box_storer= after_plac(x,y,z,end_x,perms[i][j],strip_list,container_toFit,ax,colors[perms[i][j]],curr_weight,stored_plac,row,storage_strip,prev_y,prev_row,prev_row_num,vol_occ,y_min,tmp,vol_wasted,box_storer)
            
            tmp.at[perms[i][j],'Rem_Strips'] =total_strips
            tmp.at[perms[i][j],'Marked'] = 0
        
        
        df_stored.append(tmp)
        nH_list =  []

        for m in range(len(tmp)):
            nH_list.append([tmp.at[m,'Length'],tmp.at[m,'Width'],tmp.at[m,'Height'],tmp.at[m,'Rem_Boxes'],m,tmp.at[m,'GrossWeight']])
        x,y,z,vol_occ,y_min,tmp,vol_wasted,storage_strip,nH_list = place_nonH(x,y,z,colors,nH_list,container_toFit,ax,curr_weight,stored_plac,vol_occ,y_min,tmp,vol_wasted,storage_strip)
 
        if y_min <0:
            y_min = 0       
        packaging_density = (vol_occ/(container_toFit.width*container_toFit.height*(container_toFit.length-y_min))) 
        vol_occ_curr =round(vol_occ/(container_toFit.length*container_toFit.width*container_toFit.height),2)*100
        vol_container= container_toFit.length*container_toFit.width*container_toFit.height
        perc_wasted = round(float(vol_wasted/(vol_container))*100,2)
        
        weight_leftHalf, weight_rightHalf = weight_distribution(container_toFit,storage_strip)
        stability_fin = stability(weight_leftHalf,weight_rightHalf,best_width_order,curr_order,round(vol_wasted*pow(10,-9),2),vol_occ_curr)
        if min_stab>stability_fin:
            min_stab = stability_fin
            final_df = deepcopy(tmp)
            filename = create_bottom_view(ax, i,vol_occ_curr,perc_wasted,keys,roll,stability_fin,container_num,packaging_density)
            final_filename = deepcopy(filename)

        ax.cla()

    return final_filename,final_df

    

# @app.route('/load_backend_function', methods=['POST'])
# def load_backend_function():
#     # Perform your backend function here
#     # For demonstration purposes, just printing a message

#     df_storer=[]
#     img_paths=[]
#     outer_index= 0
#     container_num=1
    
#     # Return a response if needed
#     start_time = time.time()
#     df, container_data = load_data_from_files()

#     data = deepcopy(df)
    
#     for keys, values in container_data.items():
#         selected_truck_spec = truck_specs.get(keys, {})
    
#         if outer_index==0:
#             df,container_toFit,strip_list= DataProcess(df,selected_truck_spec,1,1,data)
#         if outer_index!=0:
            
#            df,container_toFit,strip_list = DataProcess(df,selected_truck_spec,1,2,data)
#         roll = values
#         index_= 0
#         while roll>0:
#             filename,df= worker(df,container_toFit,strip_list,keys,index_,container_num)
#             container_num+=1
#             temp= deepcopy(df)
#             df_storer.append(temp.to_html(classes='data')) 
#             index_+=1
#             roll-=1
#             filename = filename.replace('\\', '/')
#             img_paths.append(filename)

#         outer_index+=1
#     # selected_truck_spec = truck_specs.get(truck_spec, {})
#     end_time = time.time()
#     print("Time_Req ", end_time-start_time)

#     response = {
#     'show_optimal_solution': True,  # Set this to True if you want to display the optimal solution
#     'df_html_array': df_storer,  # DataFrame converted to HTML format
#     'image_Array': img_paths
#     }
    

    
#     return

    



def save_data_to_files(df, truck_specifications):
    # Save DataFrame to CSV file
    df.to_csv('home/static/files/data.csv', index=False)

    # Save truck specifications to a JSON file
    with open('home/static/files/truck_specs.json', 'w') as file:
        json.dump(truck_specifications, file)

def load_data_from_files():
    # Read DataFrame from CSV file
    df = pd.read_csv('home/static/files/data.csv')

    # Read truck specifications from JSON file
    with open('home/static/files/truck_specs.json', 'r') as file:
        truck_specs = json.load(file)

    return df, truck_specs


def find_weightORvolIntensive(df, container_data):
    GrossWeight = df['Gross Weight (in KGs)']
    vol_boxes = df['Volume (in m^3)']
    num_cases = df['Number of Cases ']
    box_ratio = {}
    #find the weight or volume intensive for each box for each container    

    for i in range(len(GrossWeight)):
        gross_box = GrossWeight[i]
        vol_box = vol_boxes[i]     
        num_case = num_cases[i] 

        for keys,values in container_data.items():
            container = truck_specs.get(keys,{})
            length_container = container['length_container']
            width_container = container['width_container']
            height_container = container['height_container']
            max_weight= container['max_weight']
            vol_container = round(pow(10,-9)*(length_container*width_container*height_container),2)

            #weight_comparison
            weight_ratio = (gross_box*num_case)/max_weight

            #vol comparison
            vol_ratio = (vol_box*num_case)/vol_container
            total_weight = gross_box*num_case

            if weight_ratio > vol_ratio and total_weight > max_weight:
                box_ratio[i] = keys
    


    return box_ratio


def place_weightIntensive(df,weight_intensive):
    perc = []
    for keys, values in weight_intensive.items():
        container = truck_specs.get(values,{})
        length_container = container['length_container']
        width_container = container['width_container']
        height_container = container['height_container']


        max_weight= container['max_weight']
        area_total = length_container*width_container
        box_length = df.at[keys,'Length (in cm)']
        box_width = df.at[keys,'Width  (in cm)']
        box_height = df.at[keys,'Height  (in cm)']
        box_weight = df.at[keys,'Gross Weight (in KGs)']
        num_cases = df.at[keys,'Number of Cases ']

        num_fit= max_weight//box_weight
        if num_fit < num_cases:
            num_cases = deepcopy(num_fit)
        
        area_perBox = box_width*box_length
        num_boxes_toCover = (width_container//box_width)*(length_container//box_length)
        height_stack = num_cases//num_boxes_toCover
        if height_stack < 1:
            height_stack = 1
        
        perc_per = (height_stack*box_height)/height_container
        perc.append(perc_per)

    return perc



# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return 'No file part'
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return 'No selected file'

#     total_containers = int(request.form['totalContainers'])

#     # Retrieve the type and count of each container
#     container_data = {}
#     for i in range(1, total_containers + 1):
#         container_type = request.form['containerType{}'.format(i)]
#         if container_type == "Custom Container":
#             custom_length = int(request.form['customLength'])
#             custom_width = int(request.form['customWidth'])
#             custom_height = int(request.form['customHeight'])
#             custom_max_weight = int(request.form['customMaxWeight'])
            
#             # Add custom container specs to the truck_specs dictionary
#             truck_specs["Custom Container"] = {
#                 'length_container': custom_length,
#                 'width_container': custom_width,
#                 'height_container': custom_height,
#                 'max_weight': custom_max_weight
#                 }
#         container_count = int(request.form['containerCount{}'.format(i)])
#         container_data[container_type] = container_count


#     df = pd.read_excel(file)

#     save_data_to_files(df, container_data)
#     data = deepcopy(df)
#     df_storer = []
#     img_paths = []
#     outer_index = 0
   

#     for keys, values in container_data.items():
#         selected_truck_spec = truck_specs.get(keys, {})
#         if outer_index == 0:
#             df, container_toFit, strip_list = DataProcess(df, selected_truck_spec,1,1,data)
#         if outer_index != 0:
#             df, container_toFit, strip_list = DataProcess(df, selected_truck_spec,1,2,data)

#         roll = values
#         index_ = 0
#         while roll > 0:
#             filename, df = perform_computation(df, container_toFit, strip_list, keys, index_)
#             df_storer.append(df.to_html(classes='data'))
#             index_ += 1
#             roll -= 1
#             img_paths.append(filename)

#         outer_index += 1

#     return {tables=df_storer, img_paths=img_paths}
