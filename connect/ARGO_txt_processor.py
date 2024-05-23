import time
import os
import numpy as np
import re
import netCDF4 as nc
import seawater

class TXTProcessor:
    def extract_data(file_path):
        # 定义正则表达式 1,必有的数据
        patterns_1 = {
            'profile_number': r"PROFILE\s+NUMBER:\s+(\d+)",
            'cycle_time': r"CYCLE\s+TIME:\s+([0-9hmin]+)",
            'down_time': r"DOWN\s+TIME:\s+([0-9hmin]+)",
            'up_time': r"UP\s+TIME:\s+([0-9hmin]+)",
            'descent_start_time': r"DSCENT\s+START\s+TIME:\s+([0-9/: ]+)",
            'descent_end_time': r"DSCENT\s+END\s+TIME:\s+([0-9/: ]+)",
            'ascent_start_time': r"ASCENT\s+START\s+TIME:\s+([0-9/: ]+)",
            'ascent_end_time': r"ASCENT\s+END\s+TIME:\s+([0-9/: ]+)",
            'start_transmission_latitude': r"START\s+TRANSMISSION\s+LATITUDE\s+([0-9.]+)",
            'start_transmission_longitude': r"START\s+TRANSMISSION\s+LONGITUDE\s+([0-9.]+)",
            'finish_transmission_latitude': r"FINISH\s+TRANSMISSION\s+LATITUDE\s+([0-9.]+)",
            'finish_transmission_longitude': r"FINISH\s+TRANSMISSION\s+LONGITUDE\s+([0-9.]+)",
            'start_date_pattern': r"START\s+TRANSMISSION\s+YY/MM/DD\s+([0-9/]+)", # 出水定位中的时间
            'start_time_pattern'  : r"START\s+TRANSMISSION\s+HH:MM:SS\s+([0-9:]+)",
            'finish_date_pattern' : r"FINISH\s+TRANSMISSION\s+YY/MM/DD\s+([0-9/]+)",# 下个剖面入水定位中的时间
            'finish_time_pattern' : r"FINISH\s+TRANSMISSION\s+HH:MM:SS\s+([0-9:]+)"
        }
        # 在正则表达式中，括号具有特殊的含义，它用于表示捕获组,所以需要使用反斜杠 \ 来转义括号字符                              
        # \s表示空格，+ 表示匹配一个或多个前面的元字符，所以 \s+ 表示匹配一个或多个空白字符
        # ([0-9/: ]+): 这是一个捕获组
        # [0-9/: ] 是一个字符类，它匹配任何数字（0-9）、冒号（:）、斜杠（/）或空格（ ）

        # 定义正则表达式 2,未必有的 DRIFT数据
        patterns_2 = {
            'DRIFT_PRESSURE' : r'DRIFT\s+PRESSURE\(DBAR\):\s+([0-9.]+)',
            'DRIFT_TEMPERATURE' : r'DRIFT\s+TEMPERATURE\(DEG\s+C\):\s+([0-9.]+)',
            'DRIFT_SALINITY' : r'DRIFT\s+SALINITY\(PSU\):\s+([0-9.]+)'
        }
        # 初始化字典，分别存储：必有的数据、未必有的 DRIFT数据、profile的 3列数据
        data = {}
        profile_data = []
        matches = {key: [] for key in patterns_2.keys()}
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        profileID = lines[1].strip()[17:]
        Argo_SN = lines[3].strip()[25:]
        deviceID = lines[6].strip()[19:]
        # Iterate over each line and check against each pattern
        for line in lines:
            for key, pattern in patterns_1.items():
                match = re.search(pattern, line) 
                if match:
                    data[key] = match.group(1) # 必有的数据
            for key, pattern in patterns_2.items():
                match = re.search(pattern, line)
                if match:
                    matches[key].append(match.group(1)) # DRIFT数据
            
    
            # profile的 3列数据
            profile_line = re.findall(r"\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)", line)
            if profile_line:
                profile_data.append(profile_line[0])
                
        # 使用列表解析从每个元组中提取相应的元素
        pres = [float(data[0]) for data in profile_data]  # 提取并转换为浮点数
        salt = [float(data[1]) for data in profile_data]  # 提取并转换为浮点数
        temp = [float(data[2]) for data in profile_data]  # 提取并转换为浮点数
        pres = np.array(pres); salt = np.array(salt); temp = np.array(temp) 
        pres = np.round(pres, decimals=3); salt = np.round(salt, decimals=4); temp = np.round(temp, decimals=4)
        profile_data = [pres,salt,temp]    
        profile_data = np.vstack((profile_data[0], profile_data[1], profile_data[2])).T
        # 阈值剔除异常数据
        index_pre = profile_data[:,0] > 0
        profile_data = profile_data[index_pre]
        index_salt = (profile_data[:,1] < 41.0) &(profile_data[:,1] > 0)
        profile_data = profile_data[index_salt] 
        index_temp = (profile_data[:,2] < 40.0) & (profile_data[:,1] > -2.5)
        profile_data = profile_data[index_temp]   
        
        DRIFT = matches # DRIFT数据
        if DRIFT['DRIFT_PRESSURE'] != []: # 如果不为空，则转换为
            for key, value in DRIFT.items():
                if value:  # 检查值是否为空列表
                    DRIFT[key] = np.array(value, dtype='float64')
        else:
            print('DRIFT为空')
        DRIFT['DRIFT_PRESSURE'] = np.round(DRIFT['DRIFT_PRESSURE'],3)
        DRIFT['DRIFT_TEMPERATURE'] = np.round(DRIFT['DRIFT_TEMPERATURE'],4)
        DRIFT['DRIFT_SALINITY'] = np.round(DRIFT['DRIFT_SALINITY'],4)
        
        return data, DRIFT,profile_data,deviceID,profileID,Argo_SN



    def nc_generate(data,DRIFT,profile_data,new_path,Argo_Type = 'HM-B',deviceID = '900299',profileID = '001',lon2 = 105.21,lat2 = 15.11,Argo_SN = '319485',ReleaseTime = '2022-12-11 14:03:07 UTC',ReleaseLongitude = '111.8444°E',ReleaseLatitude = '17.4169°N',Comment = 'quality control data',information = ''):
        ### 提取必有的数据 ###
        profile_number = data['profile_number'];cycle_time = data['cycle_time'];down_time = data['down_time'];up_time =data['up_time'];descent_start_time = data['descent_start_time']; 
        descent_end_time = data['descent_end_time'];ascent_start_time = data['ascent_start_time'];ascent_end_time = data['ascent_end_time'];start_transmission_latitude = data['start_transmission_latitude'];
        start_transmission_longitude = data['start_transmission_longitude'];start_date_pattern = data['start_date_pattern'];start_time_pattern =data['start_time_pattern']; 
        finish_transmission_latitude = data['finish_transmission_latitude'];finish_transmission_longitude = data['finish_transmission_longitude']; 
        finish_date_pattern = data['finish_date_pattern'];finish_time_pattern = data['finish_time_pattern']; 
        # 开始和结束传输时的时间组合及'/'替换为'-'
        from datetime import datetime
        start_transmission_time = (start_date_pattern + ' ' + start_time_pattern).replace('/', '-')
        start_transmission_time = datetime.strptime(start_transmission_time, '%Y-%m-%d %H:%M:%S') # 解析日期时间字符串
        start_transmission_time = int(start_transmission_time.strftime('%Y%m%d%H%M%S'))

        finish_transmission_time = (finish_date_pattern + ' ' +finish_time_pattern).replace('/', '-')
        finish_transmission_time = datetime.strptime(finish_transmission_time, '%Y-%m-%d %H:%M:%S') # 解析日期时间字符串
        finish_transmission_time = int(finish_transmission_time.strftime('%Y%m%d%H%M%S'))

        # descent 和 ascent 开始和结束时间格式转化:'09/12/2023 00:01:00' 替换为 '2023-09-12 00:01:00'
        descent_start_time = datetime.strptime(descent_start_time, '%d/%m/%Y %H:%M:%S') # 解析日期时间字符串
        # descent_start_time = descent_start_time.strftime('%Y-%m-%d %H:%M:%S') # 格式化为新的字符串格式
        descent_start_time = int(descent_start_time.strftime('%Y%m%d%H%M%S')) # 转换为整数
        descent_end_time = datetime.strptime(descent_end_time, '%d/%m/%Y %H:%M:%S') # 解析日期时间字符串
        descent_end_time = int(descent_end_time.strftime('%Y%m%d%H%M%S')) # 格式化为新的字符串格式

        ascent_start_time = datetime.strptime(ascent_start_time, '%d/%m/%Y %H:%M:%S') # 解析日期时间字符串
        ascent_start_time = int(ascent_start_time.strftime('%Y%m%d%H%M%S')) # 格式化为新的字符串格式
        ascent_end_time = datetime.strptime(ascent_end_time, '%d/%m/%Y %H:%M:%S') # 解析日期时间字符串
        ascent_end_time = int(ascent_end_time.strftime('%Y%m%d%H%M%S')) # 格式化为新的字符串格式

        ### 提取上浮过程数据 ###
        # [profile_pressure,profile_salinity,profile_temperature] = profile_data
        profile_pressure = profile_data[:,0]
        profile_salinity = profile_data[:,1]
        profile_temperature = profile_data[:,2]

        import seawater
        profile_density = seawater.dens(profile_salinity, profile_temperature, profile_pressure)
        profile_sound_speed = seawater.svel(profile_salinity, profile_temperature, profile_pressure)
        profile_density = np.round(profile_density,4); profile_sound_speed = np.round(profile_sound_speed,4); 
        # 提取DRIFT数据
        if type(DRIFT['DRIFT_PRESSURE']) == np.ndarray:
            DRIFT_PRESSURE = DRIFT['DRIFT_PRESSURE']; DRIFT_PRESSURE = np.round(DRIFT_PRESSURE,3); 
            DRIFT_TEMPERATURE = DRIFT['DRIFT_TEMPERATURE']; DRIFT_TEMPERATURE = np.round(DRIFT_TEMPERATURE,4); 
            DRIFT_SALINITY = DRIFT['DRIFT_SALINITY']; DRIFT_SALINITY = np.round(DRIFT_SALINITY,4); 
            # 阈值剔除异常数据
            DRIFT_copy = np.vstack((DRIFT_PRESSURE, DRIFT_TEMPERATURE, DRIFT_SALINITY)).T
            index_pre = DRIFT_copy[:,0] > 0
            DRIFT_copy = DRIFT_copy[index_pre]
            index_temp = (DRIFT_copy[:,1] < 40.0) & (DRIFT_copy[:,1] > -2.5)
            DRIFT_copy = DRIFT_copy[index_temp]
            index_salt = (DRIFT_copy[:,2] < 41.0) &(DRIFT_copy[:,1] > 0)
            DRIFT_copy = DRIFT_copy[index_salt]
            # 剔除异常值后重新赋值给 3个变量
            DRIFT_PRESSURE = DRIFT_copy[:,0]
            DRIFT_TEMPERATURE = DRIFT_copy[:,1]
            DRIFT_SALINITY = DRIFT_copy[:,2]

            DRIFT_DENSITY = seawater.dens(DRIFT_SALINITY, DRIFT_TEMPERATURE, DRIFT_PRESSURE)
            DRIFT_SOUND_SPEED = seawater.svel(DRIFT_SALINITY, DRIFT_TEMPERATURE, DRIFT_PRESSURE)
            DRIFT_DENSITY = np.round(DRIFT_DENSITY,4); DRIFT_SOUND_SPEED = np.round(DRIFT_SOUND_SPEED,4); 
        # 创建nc文件
        format = 'NETCDF3_CLASSIC'
        last_time = str(finish_transmission_time)[:12]
        filename = f'Argo_{Argo_Type}_{deviceID}_Pro{int(profileID)}_{lon2}E_{lat2}N_{last_time}_Q.nc'
        file  = nc.Dataset(new_path+'/'+f'{filename}', 'w',format= format)
        
        # 创建维度
        profileID_dim = file.createDimension('num_profile',1)
        cycle_time_dim = file.createDimension('num_cycle',len(cycle_time))
        down_time_dim = file.createDimension('num_down',len(down_time))
        up_time_dim = file.createDimension('num_up',len(up_time))
        time_dim = file.createDimension('num_time',1) # 19变为1
        lon_dim = file.createDimension('num_longitude',1)
        lat_dim = file.createDimension('num_latitude',1)
        if type(DRIFT['DRIFT_PRESSURE']) == np.ndarray:
            drift_dim = file.createDimension('num_drift_node', len(DRIFT_PRESSURE))
        node_dim = file.createDimension('num_node',len(profile_pressure))
        
        # 创建变量
        profileID_var = file.createVariable('profile_number','i4',('num_profile',))
        cycle_time_var = file.createVariable('cycle_time','S1',('num_cycle',))
        down_time_var = file.createVariable('down_time','S1',('num_down',))
        up_time_var = file.createVariable('up_time','S1',('num_up',))
        descent_start_time_var = file.createVariable('descent_start_time','f8',('num_time',))
        descent_end_time_var = file.createVariable('descent_end_time','f8',('num_time',))
        ascent_start_time_var = file.createVariable('ascent_start_time','f8',('num_time',))
        ascent_end_time_var = file.createVariable('ascent_end_time','f8',('num_time',))
        start_transmission_longitude_var = file.createVariable('start_transmission_longitude','f4',('num_longitude',))
        start_transmission_latitude_var = file.createVariable('start_transmission_latitude','f4',('num_latitude',))
        start_transmission_time_var = file.createVariable('start_transmission_time','f8',('num_time',))
        finish_transmission_longitude_var = file.createVariable('finish_transmission_longitude','f4',('num_longitude',))
        finish_transmission_latitude_var = file.createVariable('finish_transmission_latitude','f4',('num_latitude',))
        finish_transmission_time_var = file.createVariable('finish_transmission_time','f8',('num_time',))
        if type(DRIFT['DRIFT_PRESSURE']) == np.ndarray:
            drift_pressure_var = file.createVariable('drift_pressure','f4',('num_drift_node',))
            drift_temperature_var = file.createVariable('drift_temperature','f4',('num_drift_node',))
            drift_salinity_var = file.createVariable('drift_salinity','f4',('num_drift_node',))
            drift_density_var = file.createVariable('drift_density','f4',('num_drift_node',))
            drift_sound_speed_var = file.createVariable('drift_sound_speed','f4',('num_drift_node',))
        profile_pressure_var = file.createVariable('profile_pressure','f4',('num_node',))
        profile_temperature_var = file.createVariable('profile_temperature','f4',('num_node',))
        profile_salinity_var = file.createVariable('profile_salinity','f4',('num_node',))
        profile_density_var = file.createVariable('profile_density','f4',('num_node',))
        profile_sound_speed_var = file.createVariable('profile_sound_speed','f4',('num_node',))

        # 添加属性
        profileID_var.long_name="the current profile number of Argo"
        cycle_time_var.long_name="the elapsed time for the profile of Argo"
        down_time_var.long_name = 'the elapsed time for descending of Argo' 
        up_time_var.long_name = "the elapsed time for ascending of Argo" 
        descent_start_time_var.long_name = "the start time UTC for descending of Argo"
        descent_end_time_var.long_name = " the end time UTC for descending of Argo"
        ascent_start_time_var.long_name = "the start time UTC for ascending of Argo"
        ascent_end_time_var.long_name = "the end time UTC for ascending of Argo"
        start_transmission_longitude_var.long_name = "the end longitude of current profile observed by the Argo"
        start_transmission_longitude_var.units = "degrees_east"
        start_transmission_latitude_var.long_name = "the end latitude of current profile observed by the Argo"
        start_transmission_latitude_var.units = "degrees_north"
        start_transmission_time_var.long_name = "the end time UTC of current profile observed by the Argo"
        finish_transmission_longitude_var.long_name = "the start longitude of next profile observed by the Argo"
        finish_transmission_longitude_var.units = "degrees_east"
        finish_transmission_latitude_var.long_name = "the start latitude of next profile observed by the Argo"
        finish_transmission_latitude_var.units = "degrees_north"
        finish_transmission_time_var.long_name = "the start time UTC of next profile observed by the Argo"
        if type(DRIFT['DRIFT_PRESSURE']) == np.ndarray:
            drift_pressure_var.long_name = "the seawater pressure during drifting observed by the Argo"
            drift_pressure_var.units = "dbar"
            drift_temperature_var.long_name = "the seawater temperature during drifting observed by the Argo"
            drift_temperature_var.units = "Celsius"
            drift_salinity_var.long_name = "the seawater salinity during drifting observed by the Argo"
            drift_salinity_var.units = "PSU"
            drift_density_var.long_name = "the seawater density during drifting calculated by the CTD"
            drift_density_var.units = "kg/m3"
            drift_sound_speed_var.long_name = "the seawater sound speed during drifting calculated by the CTD"
            drift_sound_speed_var.units = "m/s"
        profile_temperature_var.long_name = "a profile of seawater temperature during ascending observed by the Argo"
        profile_temperature_var.units = "Celsius"
        profile_pressure_var.long_name = "a profile of seawater pressure during ascending observed by the Argo"
        profile_pressure_var.units = "dbar"
        profile_salinity_var.long_name = "a profile of seawater salinity during ascending observed by the Argo"
        profile_salinity_var.units = "PSU"
        profile_density_var.long_name = "a profile of seawater density during ascending calculated by the CTD"
        profile_density_var.units = "kg/m3"
        profile_sound_speed_var.long_name =  "a profile of seawater sound speed during ascending calculated by the CTD"
        profile_sound_speed_var.units = "m/s"

        # 变量中写入数据
        profileID_var[:] = int(profile_number)
        cycle_time_var[:] = np.array(list(cycle_time), dtype='S1')
        down_time_var[:] = np.array(list(down_time), dtype='S1')
        up_time_var[:] = np.array(list(up_time), dtype='S1')
        descent_start_time_var[:] = descent_start_time # np.array(list(descent_start_time), dtype='S1')
        descent_end_time_var[:] = descent_end_time # np.array(list(descent_end_time), dtype='S1')
        ascent_start_time_var[:] = ascent_start_time # np.array(list(ascent_start_time), dtype='S1')
        ascent_end_time_var[:] = ascent_end_time # np.array(list(ascent_end_time), dtype='S1')
        start_transmission_longitude_var[:] = float(start_transmission_longitude)
        start_transmission_latitude_var[:] = float(start_transmission_latitude)
        start_transmission_time_var[:] = start_transmission_time # np.array(list(start_transmission_time), dtype='S1')
        finish_transmission_longitude_var[:] = float(finish_transmission_longitude)
        finish_transmission_latitude_var[:] = float(finish_transmission_latitude)
        finish_transmission_time_var[:] = finish_transmission_time # np.array(list(finish_transmission_time), dtype='S1')
        if type(DRIFT['DRIFT_PRESSURE']) == np.ndarray:
            drift_pressure_var[:] = DRIFT_PRESSURE
            drift_temperature_var[:] = DRIFT_TEMPERATURE
            drift_salinity_var[:] = DRIFT_SALINITY
            drift_density_var[:] = DRIFT_DENSITY
            drift_sound_speed_var[:] = DRIFT_SOUND_SPEED
        profile_temperature_var[:] = profile_temperature
        profile_pressure_var[:] = profile_pressure
        profile_salinity_var[:] = profile_salinity
        profile_density_var[:] = profile_density
        profile_sound_speed_var[:] = profile_sound_speed

        # 全局属性(需要放到最后来，不然添加不上全局属性)
        file.Argo_SN = Argo_SN
        file.Argo_ReleaseTime = ReleaseTime
        file.Argo_ReleaseLongitude = ReleaseLongitude
        file.Argo_ReleaseLatitude = ReleaseLatitude
        file.Sensor_accuracy = 'temperature,SBE41CP,±0.002℃;salinity,SBE41CP,±0.01m/s;pressure,SBE41CP,±0.8dbar/year'
        file.Comment = Comment
        file.Information = information
        file.Manufacturer = '青岛海山海洋装备有限公司'
        file.Source = 'Wei Ma, TianJin University, wei.ma@tju.edu.cn'
        import datetime
        import pytz
        current_time = datetime.datetime.now() # 获取当前时间
        utc_time = current_time.astimezone(pytz.utc) # 将当前时间转换为 UTC 时间
        formatted_utc_time = utc_time.strftime("%Y-%m-%d %H:%M:%S %Z") # 格式化并显示 UTC 时间
        time_now = str(formatted_utc_time)[:19]
        file.History = f'Created by Python at {time_now} UTC'

        file.close() # 关闭文件
        nc_path = new_path+'/'+f'{filename}'
        return nc_path.replace('\\', '/')