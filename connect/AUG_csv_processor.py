import pandas as pd
import os
import numpy as np
import netCDF4 as nc

class CSVProcessor:
    # 处理 CSV 文件的函数
    def process_csv(file_path):
        # 读取文件并剔除异常数据
        df = pd.read_csv(file_path,encoding='gb2312')
        df['数据时间'] = pd.to_datetime(df['数据时间'])
        index_temp = (df['CTD温度(℃)'] < 40.0) &(df['CTD温度(℃)'] > -2.5)
        df = df[index_temp]
        index_cond = (df['CTD电导率(S/m)'] < 6) &(df['CTD电导率(S/m)'] > 0)
        df = df[index_cond]
        index_salt = (df['CTD盐度(S/m)'] < 41.0) &(df['CTD盐度(S/m)'] > 0)
        df = df[index_salt]
        index_pre = df['CTD深度(m)'] > 0
        df = df[index_pre]

        # TIME = str(df['数据时间'].iloc[0])# 留着下面time备用
        df['数据时间'] = pd.to_datetime(df['数据时间'])
        df['数据时间'] = df['数据时间'].dt.strftime('%Y%m%d%H%M%S').astype('int64')
        TIME = df['数据时间'].iloc[0]
        # TIME = TIME.strftime('%Y%m%d%H%M%S').astype('int64')
        # df去除时间列，去除重复行，保持深度从小到大排序
        df = df.drop(df.columns[0], axis=1) # 数据时间
        df = df.drop(df.columns[1], axis=1) # 帧号
        df = df.drop_duplicates()
        df = df.sort_values(by='CTD深度(m)')
        return TIME,df
    
    def nc_generate(df,TIME,new_path,file_path,lon2 = 105.21,lat2 = 15.11,deploy_time =202303270530,ReleaseTime = '2022-12-11 14:03:07 UTC',ReleaseLongitude = '111.8444°E',ReleaseLatitude = '17.4169°N',CTD_SN = 2408,Comment = 'quality control data',information ='') :
        # Glider_Type:'HY-BX' lon2:105.21 lat2:15.11 deploy_time:202303270530(整数就可以，字符串也可以)
        name = file_path.split('\\')[-1] # 'Glider_HY-BX_003_Pro003_taskframe.csv'
        Glider_Type = name.split('_')[1]
        deviceID = name.split('_')[2]
        # deviceID = int(df['设备ID'].iloc[0])
        # deviceID = '{:03d}'.format(deviceID)
        profileID = df['工作剖面序号'].iloc[-1]
        lat = round(df['纬度(°)'].iloc[-1], 4)
        lon = round(df['经度(°)'].iloc[-1],4)
        depth = round(df['CTD深度(m)'],3)
        time = TIME
        temp = round(df['CTD温度(℃)'],4)
        cond = round(df['CTD电导率(S/m)'],4)
        salt = round(df['CTD盐度(S/m)'],4)
        density = round(df['CTD密度(kg/m3)'],4)
        sound = round(df['CTD声速(m/s)'],4)

        depth_len = df.shape[0] # 获取数据行数，为depth_dim准备
        # 创建nc文件
        format = 'NETCDF3_CLASSIC'
        filename = f'Glider_{Glider_Type}_{deviceID}_Pro{profileID}_{lon2}E_{lat2}N_{deploy_time}_Q.nc'
        # filename = 'Glider'+ deviceID + '-Profile' + str(profileID)
        # new_path = r'C:\Users\lenovo\Desktop\java\Glider05'
        file  = nc.Dataset(new_path+'/'+f'{filename}', 'w',format= format)

        # 创建维度
        profileID_dim = file.createDimension('num_profile',1)
        time_dim = file.createDimension('num_time',1)
        lon_dim = file.createDimension('num_longitude',1)
        lat_dim = file.createDimension('num_latitude',1)
        node_dim = file.createDimension('num_node',depth_len)
        # deviceID_dim = file.createDimension('deviceID',1)

        # 创建变量
        profileID_var = file.createVariable('profile_number','i4',('num_profile',))
        time_var = file.createVariable('end_time','f8',('num_time',)) 
        lon_var = file.createVariable('end_longitude','f4',('num_longitude',))
        lat_var = file.createVariable('end_latitude','f4',('num_latitude',))
            # 'Latitude': 这是新创建的变量的名称
            # 'f4': 这指定了变量的数据类型。'f8'代表64位浮点数（双精度）
            # ('Latitude',):指定新变量所依赖的维度，('Latitude',)创建元组，而 ('Latitude')为一个字符串

        # deviceID_var = file.createVariable('deviceID','i4',('deviceID',))
        depth_var = file.createVariable('profile_pressure','f4',('num_node',))
        temp_var = file.createVariable('profile_temperature','f4',('num_node',))
        cond_var = file.createVariable('profile_conductivity','f4',('num_node',))
        salt_var = file.createVariable('profile_salinity','f4',('num_node',))
        density_var = file.createVariable('profile_density','f4',('num_node',))
        sound_var = file.createVariable('profile_sound_velocity','f4',('num_node',))

        # 添加属性
        profileID_var.long_name="current profile number of glider"
        time_var.long_name="the end UTC time of current profile observed by the glider"
        lon_var.long_name = 'the end longitude of current profile located by the glider' 
        lon_var.units = "degrees_east" 
        lat_var.long_name = 'the end latitude of current profile located by the glider'
        lat_var.units = "degrees_north"
        depth_var.long_name = "a profile of seawater pressure during ascending observed by the glider"
        depth_var.units = "dbar"    
        temp_var.long_name = 'a profile of seawater temperature during ascending observed by the glider'
        temp_var.units = "Celsius" 
        cond_var.long_name = "a profile of seawater conductivity during ascending observed by the glider"
        cond_var.units = "S/m" 
        salt_var.long_name = "a profile of seawater salinity during ascending calculated by the CTD "
        salt_var.units = "PSU" 
        density_var.long_name =  "a profile of seawater density during ascending calculated by the CTD"
        density_var.units = "kg/m3" 
        sound_var.long_name = "a profile of seawater sound velocity during ascending calculated by the CTD"
        sound_var.units = "m/s" 

        # 变量中写入数据
            # 必须time_var[:] = time_data，不可以time_var= time_data
            # 使用createVariable方法创建一个变量后，这个变量实际上是一个特殊的对象，它代表netCDF文件中的一个数据区域。
            # time_var = time_data会改变time_var的引用，而不是修改它所代表的数据区域的内容
            # 相反，time_var[:]是用来引用该变量整个数据区域的一个“切片”
            # time_var[:] = time_data 实际上是将time_data数组中的数据复制到time_var所代表的数据区域中
        lat_var[:] = lat
        lon_var[:] = lon
        depth_var[:] = depth
        # time_char_array = np.array(list(time), dtype='S1')
        # time_var[:] = time_char_array # time_var只能使用整数索引写入，也许是数据类型'S19'的原因
        time_var[:] = time
        cond_var[:] = cond
        salt_var[:] = salt
        density_var[:] = density
        sound_var[:] = sound
        temp_var[:] = temp
        profileID_var[:] = profileID
        # deviceID_var[:] = deviceID

        # 全局属性(需要放到最后来，不然添加不上全局属性)
        file.Glider_SN = Glider_Type + '_' + deviceID
        file.Glider_ReleaseTime = ReleaseTime
        file.Glider_ReleaseLongitude = ReleaseLongitude
        file.Glider_ReleaseLatitude = ReleaseLatitude
        file.CTD_SN = CTD_SN
        file.Sensor_accuracy = 'temperature,Seabird GPCTD,±0.002℃;conductivity,Seabird GPCTD,±0.0003S/m;pressure,Seabird GPCTD,±0.1% of full scale range'
        file.Comment = Comment
        file.Information = information
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