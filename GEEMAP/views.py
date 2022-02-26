from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login

from .forms import CustomUser, PolygonForm, PointForm

import ee
import folium
import math
import json
import geemap.foliumap as geemap
import numpy as np
import geopandas as gpd

from .helper import add_ratio_lin, lin_to_db2, lin_to_db
from .wrapper import s1_preproc

coordenadas = []

class map(TemplateView): 
    ee.Initialize()
    template_name = 'map.html'
    
    def get_context_data(request):

        if len(coordenadas) > 0:
            Draw_in_map = True
            stud_obj = json.loads(coordenadas[0])

            new_coords = stud_obj['geometry']['coordinates']

        else:
            Draw_in_map = False

        ## Fecha más reciente
        '''proveedor = ee.ImageCollection("COPERNICUS/S1_GRD")

        rango = proveedor.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])

        recent = ee.Date(rango.get('max'))

        ff = recent.format(None, 'GMT')

        date_recent = ff.getInfo()

        date_r = date_recent.split('T')

        date_r = date_r[0]'''

        ## Interactive map

        figure = folium.Figure()
        
        Map = geemap.Map(plugin_Draw = True, 
                         Draw_export = False,
                         plugin_LayerControl = False,
                         location = [4.3, -76.1],
                         zoom_start = 10)
        
        #Map.add_shapefile(in_shp = './media/FC_PWP_map_geo.shp', layer_name = 'PMP y CC')
        
        if Draw_in_map == True:
            
            geometry_user = ee.Geometry.Polygon(new_coords)
            
            parameter = {'START_DATE': "2022-02-11",
                    'STOP_DATE' : "2022-02-23",#date_r,
                    'POLARIZATION' : 'VVVH',
                    'ORBIT' : 'BOTH',
                    'ORBIT_NUM' : None,
                    'PLATFORM_NUMBER' : None,
                    'ROI': geometry_user,
                    #2. Additional Border noise correction
                    'APPLY_ADDITIONAL_BORDER_NOISE_CORRECTION' : True,
                    #3.Speckle filter
                    'APPLY_BORDER_NOISE_CORRECTION': True,
                    'APPLY_SPECKLE_FILTERING' : True,
                    'SPECKLE_FILTER_FRAMEWORK' : 'MULTI',
                    'SPECKLE_FILTER' : 'BOXCAR',
                    'SPECKLE_FILTER_KERNEL_SIZE' : 15,
                    'SPECKLE_FILTER_NR_OF_IMAGES' : 10,
                    #4. Radiometric terrain normalization
                    'APPLY_TERRAIN_FLATTENING' : True,
                    'DEM' : ee.Image('USGS/SRTMGL1_003'),
                    'TERRAIN_FLATTENING_MODEL' : 'VOLUME',
                    'TERRAIN_FLATTENING_ADDITIONAL_LAYOVER_SHADOW_BUFFER' : 0,
                    #5. Output
                    'FORMAT' : 'DB',
                    'CLIP_TO_ROI' : False}

            s1_preprocces = s1_preproc(parameter)
            
            #Function to get yyy.mmss (float)
            def msToFrac(ms):
                year = ee.Date(ms).get('year')
                frac = ee.Date(ms).getFraction('year')
                return year.add(frac)

            #This add DATE IN FULL FORMAT. date 1 is not gonna be added.
            def xx(i):
                return i.set('date1', ee.Date(i.get('system:time_start'))).set('date2', msToFrac(i.get('system:time_start')))

            #s1_preprocces = s1_preprocces.map(lambda i: xx(i))

            s1_preprocces = s1_preprocces.map(xx)
            #print(s1_preprocces)

            #This function adds a band representing the image timestamp.
            def addTime(i):
                return i.addBands(i.metadata('date2'))

            s1_preprocces_final = s1_preprocces.map(addTime)

            ##----------------------------##
            visparam = {}

            if parameter['POLARIZATION'] == 'VVVH':
                if parameter['FORMAT'] == 'DB':
                    s1_preprocces_view = s1_preprocces.map(add_ratio_lin).map(lin_to_db2)
                    visparam['bands'] = ['VV', 'VH', 'VVVH_ratio']
                    visparam['min'] = [-20, -25, 1]
                    visparam['max'] = [0, -5, 15]
                else:
                    s1_preprocces_view = s1_preprocces.map(add_ratio_lin)
                    visparam['bands'] = ['VV', 'VH', 'VVVH_ratio']
                    visparam['min'] = [0.01, 0.0032, 1.25]
                    visparam['max'] = [1, 0.31, 31.62]
            else:
                if parameter['FORMAT'] == 'DB':
                    s1_preprocces_view = s1_preprocces.map(lin_to_db)
                    visparam['bands'] = parameter['POLARIZATION']
                    visparam['min'] = -25
                    visparam['max'] = 0
                else:
                    s1_preprocces_view = s1_preprocces
                    visparam['bands'] = parameter['POLARIZATION']
                    visparam['min'] = 0
                    visparam['max'] = 0.2
                    
            def Centroid(array):
                length = array.shape[0]
                sum_x = np.sum(array[:, 0])
                sum_y = np.sum(array[:, 1])
                return sum_x/length, sum_y/length
            
            array = np.array(new_coords[0])
            
            centroide = Centroid(array = array)
            
            geojson_test = {
            "type": "FeatureCollection",
            "columns": {
                "Place": "String",
                "system:index" : "String",
                "ID": "Long",
                "Tree" : "String"
            },
            "features": [
                {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        centroide[0],
                        centroide[1]
                    ]
                },
                "id": "0",
                "properties": {
                    "Place" : "Choice",
                    "ID" : "1"
                }
                }  
            ]
            }

            geojsonFc = ee.FeatureCollection(geojson_test)
            
            def images(img):
                return img.sampleRegions(collection = geojsonFc, scale = 10, geometries = True)

            table = ee.FeatureCollection(s1_preprocces_final.map(images)).flatten()

            table_info = table.getInfo()

            VH = table_info['features'][0]['properties']['VH']
            angle = table_info['features'][0]['properties']['angle']
            
            def sm_wcm(sigma0, theta):
                A = 85.71200708
                B = -32.46500098
                C = 0.90101068
                D = 4.39382781
                V = -0.06860272

                #Equation (2) in Bousbih's 2018 study
                thao2 = math.exp(-2 * B * (V / math.cos(theta * (math.pi / 180))))

                #Equation (4) in Bousbih's 2018 study
                sigma_0_veg = A * V * math.cos(theta * math.pi / 180) * (1 - thao2)
                sigma_0_veg = 0 if sigma_0_veg < 0 else sigma_0_veg

                #sigma_0_veg_soil was set as zero
                sigma_0_veg_soil = 0

                #Inverted form of Equation (4) in Bousbih's 2018 study, in which the equation 
                # is solved for mv (volumetric soil moisture) 

                mv = 1 / D * math.log10((sigma0 - sigma_0_veg - sigma_0_veg_soil) / (C * thao2))

                return mv
            
            model_5 = sm_wcm(sigma0 = VH, theta = angle)
            
            def theta_0_5_to_0_60(theta_0_5, lat, long):
                #Computing theta_0_60
                theta_0_60 = 0.22318 * theta_0_5 - 1.18155 * lat  +2.27015 * long + 178.43681
                return theta_0_60
            
            model_60 = theta_0_5_to_0_60(theta_0_5 = model_5, lat = centroide[1], long = centroide[0])
            
            print(f'Modelo a 60cm: {model_60}')
            
            shapefile = gpd.read_file('./media/FC_PWP_v2_map_geo.shp')

            def coord_lister(geom):
                coords = list(geom.exterior.coords)
                return (coords)

            coordinates_list = shapefile.geometry.apply(coord_lister)

            difference = []

            for i in range(len(coordinates_list)):
                centroides = Centroid(np.array(coordinates_list[i]))
                longitude, latitude = centroides[0], centroides[1]
                cenLat, cenLong = centroide[1], centroide[0]
                
                result = (((abs(longitude)-abs(cenLong))**2+((abs(latitude)-abs(cenLat))**2))**0.5)
                difference.append(result)
            
            counter = -1
            for i in difference:
                counter += 1
                if i == min(difference):
                    break
                
            
            depletion_factor = 0.5
            
            theta_FC = shapefile["CC"][counter] / 100
            
            theta_PWP = shapefile["PMP"][counter] /100

            print(f'Capacidad de campo: {theta_FC}')
            print(f'Punto de marchitez permanente: {theta_PWP}')
            
            if model_60 <= theta_FC:
                
                #Total and readly avaible water
                taw = theta_FC - theta_PWP
                raw = taw * depletion_factor * 600
                print("taw", taw)
                print("raw", raw)
                
                lam = 600 * (theta_FC - model_60)
                
                
                if lam >= raw:
                    #Red color
                    color_alert = 'Red'
                else:
                    #Yellow color
                    color_alert = 'Yellow'        
            else:
                # Green color
                lam = 0
                color_alert = 'Green'
            
            #Map.addLayer(s1_preprocces_view.first(), visparam, 'Processed_image', True, 0.5)

            sentinel1 = ee.Image(ee.ImageCollection('COPERNICUS/S1_GRD') 
                       .filterBounds(geometry_user) 
                       .filterDate(ee.Date('2022-02-11'), ee.Date('2022-02-23')) 
                       .first() 
                       .clip(geometry_user))
            
            Map.addLayer(sentinel1, {'min': [-20, -25, 1], 'max': [0, -5, 15]}, 'Plygon image', True)

            Map.addLayer(geometry_user, {'color': 'FF0000'}, 'geodesic polygon', True, 0.2)

            Map.setCenter(centroide[0],centroide[1], zoom = 16)

            Map.add_to(figure)

            figure.render()

            format_date = "2022-02-23"#date_r

            print(color_alert)

            return {"map": figure,
                    "actual_date" : format_date,
                    "color_alert" : color_alert,
                    "lamina" : round(lam, 2)}
            
        else:
            geometry = ee.Geometry.Polygon(
                [[[-76.25925273198507, 4.4784853333279475],
                [-76.86899394292257, 3.5195334529660314],
                [-76.59433573979757, 3.2947119593342977],
                [-75.99008769292257, 4.3579948778381965]]])
            
            parameter = {'START_DATE': "2022-02-11",
                    'STOP_DATE' : "2022-02-23",#date_r,
                    'POLARIZATION' : 'VVVH',
                    'ORBIT' : 'BOTH',
                    'ORBIT_NUM' : None,
                    'PLATFORM_NUMBER' : None,
                    'ROI': geometry,
                    #2. Additional Border noise correction
                    'APPLY_ADDITIONAL_BORDER_NOISE_CORRECTION' : True,
                    #3.Speckle filter
                    'APPLY_BORDER_NOISE_CORRECTION': True,
                    'APPLY_SPECKLE_FILTERING' : True,
                    'SPECKLE_FILTER_FRAMEWORK' : 'MULTI',
                    'SPECKLE_FILTER' : 'BOXCAR',
                    'SPECKLE_FILTER_KERNEL_SIZE' : 15,
                    'SPECKLE_FILTER_NR_OF_IMAGES' : 10,
                    #4. Radiometric terrain normalization
                    'APPLY_TERRAIN_FLATTENING' : True,
                    'DEM' : ee.Image('USGS/SRTMGL1_003'),
                    'TERRAIN_FLATTENING_MODEL' : 'VOLUME',
                    'TERRAIN_FLATTENING_ADDITIONAL_LAYOVER_SHADOW_BUFFER' : 0,
                    #5. Output
                    'FORMAT' : 'DB',
                    'CLIP_TO_ROI' : False}

            s1_preprocces = s1_preproc(parameter)

            #Function to get yyy.mmss (float)
            def msToFrac(ms):
                year = ee.Date(ms).get('year')
                frac = ee.Date(ms).getFraction('year')
                return year.add(frac)

            #This add DATE IN FULL FORMAT. date 1 is not gonna be added.
            def xx(i):
                return i.set('date1', ee.Date(i.get('system:time_start'))).set('date2', msToFrac(i.get('system:time_start')))

            #s1_preprocces = s1_preprocces.map(lambda i: xx(i))

            s1_preprocces = s1_preprocces.map(xx)
            #print(s1_preprocces)

            #This function adds a band representing the image timestamp.
            def addTime(i):
                return i.addBands(i.metadata('date2'))

            s1_preprocces_final = s1_preprocces.map(addTime)

            ##----------------------------##
            visparam = {}

            if parameter['POLARIZATION'] == 'VVVH':
                if parameter['FORMAT'] == 'DB':
                    s1_preprocces_view = s1_preprocces.map(add_ratio_lin).map(lin_to_db2)
                    visparam['bands'] = ['VV', 'VH', 'VVVH_ratio']
                    visparam['min'] = [-20, -25, 1]
                    visparam['max'] = [0, -5, 15]
                else:
                    s1_preprocces_view = s1_preprocces.map(add_ratio_lin)
                    visparam['bands'] = ['VV', 'VH', 'VVVH_ratio']
                    visparam['min'] = [0.01, 0.0032, 1.25]
                    visparam['max'] = [1, 0.31, 31.62]
            else:
                if parameter['FORMAT'] == 'DB':
                    s1_preprocces_view = s1_preprocces.map(lin_to_db)
                    visparam['bands'] = parameter['POLARIZATION']
                    visparam['min'] = -25
                    visparam['max'] = 0
                else:
                    s1_preprocces_view = s1_preprocces
                    visparam['bands'] = parameter['POLARIZATION']
                    visparam['min'] = 0
                    visparam['max'] = 0.2
                    
            #Map.addLayer(s1_preprocces_view.first(), visparam, 'Processed_image', True, 0.5)

            color_alert = 'White'

            lam = None

            Map.add_to(figure)

            figure.render()

            format_date = "2022-02-23"#date_r

            print(color_alert)

            return {"map": figure,
                    "actual_date" : format_date,
                    "color_alert" : color_alert,
                    "lamina" : lam}

## Definir poligono

def polygon(request):
    if request.method == 'POST':
        form = PolygonForm(request.POST)
        if form.is_valid():
            enter_polygon = form.cleaned_data['enter_polygon']

            if len(coordenadas) > 0:
                coordenadas.clear()

            coordenadas.append(enter_polygon)
            
            return redirect(to = "map")
    else:
        form = PolygonForm()
    
    return render(request, 'polygon.html', {'form':form})

## Configurar punto

def point(request):
    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data['Latitud']
            lon = form.cleaned_data['fLongitud']
            
            return redirect(to = "map")
    else:
        form = PointForm()
    return render(request, 'point.html', {'form':form})

## Registro de usuario
def register_user(request):
    data = { 'form': CustomUser()}
    if request.method == 'POST':
        formulario = CustomUser(data = request.POST)
        if formulario.is_valid():
            formulario.save()

            user = authenticate(username = formulario.cleaned_data["username"], password = formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, "El usuario a sido creado satisfactoriamente")

            return redirect(to = "map")

        data["form"] = formulario    
    return render(request, 'registration/register.html', data)

    