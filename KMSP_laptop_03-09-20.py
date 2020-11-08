#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import urllib.request
import json
from dict_digger import dig
import datetime
import time
from astral import Astral
from datetime import timedelta


while True:
    #Setting current date and time in various formats for use in the script
    now = datetime.datetime.now()
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    month_full = now.strftime("%B")
    day = int(now.strftime("%d"))
    hour_24 = int(now.strftime("%H"))
    minute_24 = int(now.strftime("%M"))

    #Calculates how many minutes past midnight it is in the day
    mins_1 = (hour_24*60)
    total_mins = int(mins_1+minute_24)

    #Prints out every temperature report for today since midnight local time
    #then finds the highest and lowest values and assigns them as the high and low temperature for today, respectively
    g = urllib.request.urlopen('http://api.synopticdata.com/v2/stations/timeseries?stid=KMSP&vars=air_temp&units=english&qc_remove_data=mark&token=8c96805fbf854373bc4b492bb3439a67&obtimezone=local&recent=%s&output=json' % (total_mins))
    json_string_g = g.read()
    parsed_json_g = json.loads(json_string_g)

    for each in parsed_json_g['STATION']:
        observations_g = each['OBSERVATIONS']
        all_temps = dig(observations_g, 'air_temp_set_1')
        all_temps = list(filter(None, all_temps))

        max_temp_float_f = max(all_temps)
        min_temp_float_f = min(all_temps)
        max_temp_f = "{:.1f}".format(max_temp_float_f)
        min_temp_f = "{:.1f}".format(min_temp_float_f)
        max_temp_c = "{:.1f}".format((max_temp_float_f-32)*(5/9))
        min_temp_c = "{:.1f}".format((min_temp_float_f-32)*(5/9))

        if max_temp_f == -0.0:
            max_temp_f = 0.0

        if min_temp_f == -0.0:
            min_temp_f = 0.0


    #Gets the daily precipitation accumulation and assigns the appropriate mm and inch variables
    #If no precip for today, then precip = 0 for use later on when writing variables to files
    h = urllib.request.urlopen('http://api.synopticdata.com/v2/stations/precip?token=8c96805fbf854373bc4b492bb3439a67&stid=KMSP&recent=%s&output=json' % (total_mins))
    json_string_h = h.read()
    parsed_json_h = json.loads(json_string_h)

    precip_check_init = dig(parsed_json_h, 'SUMMARY')
    precip_check = dig(precip_check_init, 'RESPONSE_MESSAGE')

    if 'No stations found for this request' in precip_check:
        precip = 0
    else:
        for each in parsed_json_h['STATION']:
            observations_h = each['OBSERVATIONS']
            observations_h_str = str(observations_h)
            precip_mm = dig(observations_h, 'total_precip_value_1')
            precip_in = "{:.2f}".format((precip_mm*0.0393701))
            precip = 1


    #Gets Lat/Long information for Minneapolis, MN and assigns sunrise/sunset for current day
    city_name = 'Minneapolis'
    a = Astral()
    a.solar_depression = 'civil'
    city = a[city_name]

    timezone = city.timezone

    sun = city.sun(date=datetime.date(year, month, day), local=True)

    sunrise = str(sun['sunrise'])
    sunset = str(sun['sunset'])

    rise_hour = int((sunrise[12:13]))
    rise_minute = int((sunrise[14:16]))

    set_hour_24 = int((sunset[11:13]))
    set_minute_int = int((sunset[14:16]))
    set_minute_str = (sunset[14:16])
    set_hour_12 =((set_hour_24)-12)


    #Subtracts sunrise from sunset and reports daylight hours for current day
    t1 = timedelta(hours=rise_hour, minutes=rise_minute)
    t2 = timedelta(hours=set_hour_24, minutes=set_minute_int)

    daylight_hrs_full = str((t2 - t1))
    daylight_hr = int((daylight_hrs_full[0]))
    #daylight_min = int((daylight_hrs_full[3:5]))
    #print(daylight_hrs_full)
    



    #Gets the local observations from KMSP ASOS station
    f = urllib.request.urlopen('http://api.synopticdata.com/v2/stations/latest?token=8c96805fbf854373bc4b492bb3439a67&stid=KMSP&complete=1&units=english&output=json')
    json_string = f.read()
    parsed_json = json.loads(json_string)

    for each in parsed_json['STATION']:
        observations = each['OBSERVATIONS']



    #Read the current weather variables from the JSON and assign them to their appropriate variables...
        temp_f_init = dig(observations, 'air_temp_value_1')
        temp_f_float = dig(temp_f_init, 'value')
        temp_f = "{:.1f}".format(temp_f_float)

        if temp_f == -0.0:
            temp_f = 0.0

        temp_c = "{:.1f}".format((temp_f_float-32)*(5/9))

        dewp_f_init = dig(observations, 'dew_point_temperature_value_1')
        dewp_f_float = dig(dewp_f_init, 'value')
        dewp_f = "{:.1f}".format(dewp_f_float)

        if dewp_f == -0.0:
            dewp_f = 0.0

        dewp_c_float = ((dewp_f_float-32)*(5/9))
        dewp_c = "{:.1f}".format(dewp_c_float)

        wind_kt_init = dig(observations, 'wind_speed_value_1')
        wind_kt_float = dig(wind_kt_init, 'value')
        wind_mph_float = (wind_kt_float*1.15078)
        wind_mph = "{:.1f}".format(wind_mph_float)

        wind_kph = "{:.1f}".format(1.852*wind_kt_float)

        wind_dir_init = dig(observations, 'wind_cardinal_direction_value_1d')
        wind_dir = dig(wind_dir_init, 'value')

        windchill_f_float = (35.74+0.6215*temp_f_float-35.75*wind_mph_float**0.16+0.4275*temp_f_float*wind_mph_float**0.16)
        windchill_f = "{:.1f}".format(windchill_f_float)
        windchill_c_float = ((windchill_f_float-32)*(5/9))
        windchill_c = "{:.1f}".format(windchill_c_float)
        
        #Current snow depth
        snow_depth_init = dig(observations, 'snow_depth_value_1')
        snow_depth_inch = dig(snow_depth_init, 'value')
        snow_depth_cm_float = (snow_depth_inch*2.54)
        snow_depth_cm = "{:.1f}".format(snow_depth_cm_float)

        #pressure_mb_init = dig(observations, 'pressure_value_1d')
        #pressure_mb = dig(pressure_mb_init, 'value')
        #pressure_in = "{:.2f}".format(pressure_mb*0.02953)
        #print(pressure_mb)
        
        sealevel_pressure_init = dig(observations, 'sea_level_pressure_value_1d')
        sealevel_pressure = dig(sealevel_pressure_init, 'value')
        sealevel_pressure_in = "{:.2f}".format(sealevel_pressure*0.02953)

        hum_init = dig(observations, 'relative_humidity_value_1')
        humidity_float = dig(hum_init, 'value')
        humidity = "{:.1f}".format(humidity_float)
        
        heat_index_init = 0.5*(temp_f_float+61.0+((temp_f_float-68.0)*1.2)+(humidity_float*0.094))
        index_check = (temp_f_float+heat_index_init)/2
        
        #Heat index calculations
        if index_check >= 80:
            heat_index = -42.379+2.04901523*temp_f_float+10.14333127*humidity_float-.22475541*temp_f_float*humidity_float-.00683783*temp_f_float*temp_f_float-.05481717*humidity_float*humidity_float+.00122874*temp_f_float*temp_f_float*humidity_float+.00085282*temp_f_float*humidity_float*humidity_float-.00000199*temp_f_float*temp_f_float*humidity_float*humidity_float
            heat_index_code = 1
    
            if humidity_float < 13 and temp_f_float >= 80 and temp_f_float < 112:
                heat_index_f_float = heat_index - (((13-humidity_float)/4)*SQRT((17-ABS(temp_f_float-95))/17))
                heat_index_f = "{:.1f}".format(heat_index_f_float)
                heat_index_c = "{:.1f}".format((heat_index_f_float-32)*(5/9))
        
            elif humidity_float > 85 and temp_f_float >=80 and temp_f_float < 87:
                heat_index_f_float = heat_index + (((humidity_float-85)/10)*((87-temp_f_float)/5))
                heat_index_f = "{:.1f}".format(heat_index_f_float)
                heat_index_c = "{:.1f}".format((heat_index_f_float-32)*(5/9))
        
        else:
            heat_index = 'None'
            heat_index_code = 0

        wx_init = dig(observations, 'weather_condition_value_1d')
        current_wx = dig(wx_init, 'value')

        metar_init = dig(observations, 'metar_value_1')
        metar = dig(metar_init, 'value')

        altimeter_init = dig(observations, 'altimeter_value_1')
        altimeter_in = dig(altimeter_init, 'value')

        altimeter_mb = "{:.1f}".format(altimeter_in/0.029530)

        pressure_init = dig(observations, 'pressure_value_1d')
        pressure_mb = dig(pressure_init, 'value')

        wind_full = "Wind: %s at %s MPH (%s KPH)" % (wind_dir, wind_mph, wind_kph) 



        #Interpreting the METAR and outputting the current weather conditions

        if '-RA' in metar:
            current_wx = 'Light rain'

        elif 'RA' in metar:
            current_wx = 'Rain' 

        elif '+RA' in metar:
            current_wx = 'Heavy rain'   

        elif '-SH' in metar:
            current_wx = 'Light showers'

        elif 'SH' in metar:
            current_wx = 'Showers'

        elif '+SH' in metar:
            current_wx = 'Heavy showers'

        elif '-FZRA' in metar:
            current_wx = 'Light freezing rain'

        elif 'FZRA' in metar:
            current_wx = 'Freezing rain'

        elif '+FZRA' in metar:
            current_wx = 'Heavy freezing rain'

        elif '-DZ' in metar:
            current_wx = 'Light drizzle'

        elif 'DZ' in metar:
            current_wx = 'Drizzle'  

        elif '-FZDZ' in metar:
            current_wx = 'Light freezing drizzle'  

        elif 'FZDZ' in metar:
            current_wx = 'Freezing drizzle'     

        elif '+FZDZ' in metar:
            current_wx = 'Heavy freezing drizzle'  

        elif '-SN' in metar:
            current_wx = 'Light snow'

        elif 'SN' in metar:
            current_wx = 'Snow'

        elif '+SN' in metar:
            current_wx = 'Heavy snow'

        elif 'BLSN' in metar:
            current_wx = 'Blowing snow'

        elif 'TS' in metar:
            current_wx = 'Thunderstorms'

        elif 'IC' in metar:
            current_wx = 'Ice crystals'

        elif 'HZ' in metar:
            current_wx = 'Haze'

        elif 'SG' in metar:
            current_wx = 'Snow grains'

        elif 'PL' in metar:
            current_wx = 'Ice pellets'  

        elif 'FZFG' in metar:
            current_wx = 'Freezing fog' 

        elif 'BR' in metar:
            current_wx = 'Mist'

        else:
            current_wx = 0

    #If no weather currently reported, get the sky conditions instead
        if current_wx == 0:

            if 'CLR' in metar:
                current_cld = 'Clear'

            elif 'FEW' in metar:
                current_cld = 'Few clouds'

            elif 'SCT' in metar:
                current_cld = 'Scattered clouds'

            elif 'BKN' in metar:
                current_cld = 'Broken clouds'

            elif 'OVC' in metar:
                current_cld = 'Overcast'



        #Visibility conditions
        vis_init = dig(observations, 'visibility_value_1')
        vis = dig(vis_init, 'value')
        vis_km = "{:.1f}".format(vis*1.60934)


        #Write the variables to their appropriate text files:
        with open('/Users/bradh/Dropbox/Wxscript/temperature.txt','w') as f:
            f.write("Temperature: %s° F (%s° C)" % (temp_f, temp_c))

        with open('/Users/bradh/Dropbox/Wxscript/dewpoint.txt','w') as f:
            f.write("Dew point: %s° F (%s° C)" % (dewp_f, dewp_c))

        if wind_mph_float <= 1.0:
            with open('/Users/bradh/Dropbox/Wxscript/wind_speed.txt','w') as f:
                f.write('Wind: Calm')

            with open('/Users/bradh/Dropbox/Wxscript/windchill.txt','w') as f:
                f.write("Wind chill: None")
            
        elif wind_mph_float > 1.0:
            with open('/Users/bradh/Dropbox/Wxscript/wind_speed.txt','w') as f:
                f.write(wind_full)

            with open('/Users/bradh/Dropbox/Wxscript/windchill.txt','w') as f:
                f.write("Wind chill: %s° F (%s° C)" % (windchill_f, windchill_c))
                
        if heat_index_code == 1:
                
            with open('/Users/bradh/Dropbox/Wxscript/heat_index.txt','w') as f:
                f.write("Heat index: %s° F (%s° C)" % (heat_index_f, heat_index_c))
                
        else:
            with open('/Users/bradh/Dropbox/Wxscript/heat_index.txt','w') as f:
                f.write("Heat index: None")   

        with open('/Users/bradh/Dropbox/Wxscript/humidity.txt','w') as f:
            f.write("Humidity: %s%%" % (humidity))

        #with open('/Users/Brad/Wxscript/pressure.txt','w') as f:
            #f.write("Pressure: %s in (%s mb)" % (pressure_in, pressure_mb))
                                     
        with open('/Users/bradh/Dropbox/Wxscript/sealevel_pressure.txt','w') as f:
            f.write("Sea level pressure: %s mb" % (sealevel_pressure))

        with open('/Users/bradh/Dropbox/Wxscript/high_temp.txt','w') as f:
            f.write("High temperature: %s° F (%s° C)" % (max_temp_f, max_temp_c))

        with open('/Users/bradh/Dropbox/Wxscript/low_temp.txt','w') as f:
            f.write("Low temperature: %s° F (%s° C)" % (min_temp_f, min_temp_c))

        with open('/Users/bradh/Dropbox/Wxscript/visibility.txt','w') as f:
            f.write("Visibility: %s mi (%s km)" % (vis, vis_km))

        #Daylight hours (no longer using, 11-7-19)    
        #with open('/Users/Brad/Wxscript/daylight.txt','w') as f:
            #f.write("Daylight hours: %s hours, %s minutes" % (daylight_hr, daylight_min))

        with open('/Users/bradh/Dropbox/Wxscript/month_day.txt','w') as f:
            f.write("Daily statistics for %s %s:" % (month_full, day))

        #Conditional statement for 24-hour precip: if precip obs = 0, then no precip accumulation. Otherwise print precip accumulation.
        if precip == 0:
            with open('/Users/bradh/Dropbox/Wxscript/precip_24.txt','w') as f:
                f.write("Precipitation: None")
        else:
            with open('/Users/bradh/Dropbox/Wxscript/precip_24.txt','w') as f:
                f.write("Precipitation: %s in (%s mm)" % (precip_in, precip_mm))

        #If weather is not being reported, then report cloud cover. If weather is reported, show current weather condition.        

        if current_wx != 0:
            with open('/Users/bradh/Dropbox/Wxscript/weather.txt','w') as f:
                f.write("Current weather: %s" % (current_wx))
        else:
            with open('/Users/bradh/Dropbox/Wxscript/weather.txt','w') as f:
                f.write("Current weather: %s" % (current_cld))    

        with open('/Users/bradh/Dropbox/Wxscript/snowdepth.txt','w') as f:
            f.write("Snow depth: %s in (%s cm)" % (snow_depth_inch, snow_depth_cm))

        #Finally writing the sunrise and sunset to a file:

        with open('/Users/bradh/Dropbox/Wxscript/sunset.txt','w') as f:
            f.write("Sunset:  %s:%s PM CDT" % (set_hour_12, set_minute_str))

        with open('/Users/bradh/Dropbox/Wxscript/sunrise.txt','w') as f:
            f.write("Sunrise: %s:%s AM CDT" % (rise_hour, rise_minute))

        updated = now.strftime("%m/%d/%Y %I:%M %p")

        with open('/Users/bradh/Dropbox/Wxscript/updated.txt','w') as f:
            f.write("Last updated: %s" % (updated))

        print("The script was last updated: %s" % (updated))
        
        time.sleep(600)


# In[ ]:




