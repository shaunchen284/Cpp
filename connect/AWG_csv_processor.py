import pandas as pd
import numpy as np
import netCDF4 as nc

# 处理 CSV 文件的函数
def process_csv(file_path):
    # 读取文件并剔除异常数据
    df = pd.read_csv(file_path,encoding='gb2312')
    df = df[['时间','位置-经度', '位置-纬度','气温','气压','湿度','风速','风向','最大风速','最大风速对应风向','水温']]
    df['时间'] = pd.to_datetime(df['时间'])
    # 将日期时间转换为所需的数字格式  2024-04-20 05:31:00 -> 20240420053100
    df['时间'] = df['时间'].dt.strftime('%Y%m%d%H%M%S').astype('int64')
    index_temp = (df['水温'] < 40.0)&(df['水温'] > -2.5)
    df = df[index_temp]
    return df

def nc_generate(df,new_path,file_path,lon2 = 105.21,lat2 = 15.11,deploy_time =202303270530,ReleaseTime = '2022-12-11 14:03:07 UTC',ReleaseLongitude = '111.8444°E',ReleaseLatitude = '17.4169°N',Comment = 'quality control data',information ='') :
    # AWG_Type:'HZZ' lon2:105.21 lat2:15.11 deploy_time:202303270530(整数就可以，字符串也可以)
    name = file_path.split('\\')[-1] # 'AWG_HYY_003_202303270530.csv'
    AWG_Type = name.split('_')[1]
    deviceID = name.split('_')[2]
    
    time = df['时间']
    lon = round(df['位置-经度'].iloc[-1],4)
    lat = round(df['位置-纬度'].iloc[-1], 4) 
    ssat = round(df['气温'],2)
    ssap = round(df['气压'],4)
    rh = round(df['湿度'],4)
    true_wind_speed = round(df['风速'],2)
    true_wind_dir = round(df['风向'],2)
    max_wind_speed = round(df['最大风速'],2)
    max_wind_dir = round(df['最大风速对应风向'],2)
    seawater_temperature = round(df['水温'],2)

    num_row = df.shape[0] # 获取数据行数，为 node_dim准备
    # 创建nc文件
    format = 'NETCDF3_CLASSIC'
    filename = f'AWG_{AWG_Type}_{deviceID}_{lon2}E_{lat2}N_{deploy_time}_Q.nc'
    file  = nc.Dataset(new_path+'/'+f'{filename}', 'w',format= format)

    # 创建维度
    node_dim = file.createDimension('num_node',num_row)
    lon_dim = file.createDimension('num_longitude',1)
    lat_dim = file.createDimension('num_latitude',1)
    time_dim = file.createDimension('num_time',num_row)

    # 创建变量
    time_var = file.createVariable('time','f8',('num_time',))
    lon_var = file.createVariable('longitude','f4',('num_longitude',))
    lat_var = file.createVariable('latitude','f4',('num_latitude',))
        # 'Latitude': 这是新创建的变量的名称
        # 'f4': 这指定了变量的数据类型。'f8'代表64位浮点数（双精度）
        # ('Latitude',):指定新变量所依赖的维度，('Latitude',)创建元组，而 ('Latitude')为一个字符串
    ssat_var = file.createVariable('ssat','f4',('num_node',))
    ssap_var = file.createVariable('ssap','f4',('num_node',))
    rh_var = file.createVariable('rh','f4',('num_node',))
    true_wind_speed_var = file.createVariable('true_wind_speed','f4',('num_node',))
    true_wind_dir_var = file.createVariable('true_wind_dir','f4',('num_node',))
    max_wind_speed_var = file.createVariable('max_wind_speed','f4',('num_node',))
    max_wind_dir_var = file.createVariable('max_wind_dir','f4',('num_node',))
    seawater_temperature_var = file.createVariable('seawater_temperature','f4',('num_node',))

    # 添加属性
    time_var.long_name="the time observed by waveglider"
    lon_var.long_name = 'the longitude located by the waveglider' 
    lon_var.units = "degrees_east" 
    lat_var.long_name = 'the latitude located by the waveglider'
    lat_var.units = "degrees_north"
    ssat_var.long_name = "the sea surface air temperature observed by the waveglider"
    ssat_var.units = "Celsius"
    ssap_var.long_name = "the sea surface air pressure observed by the waveglider"
    ssap_var.units = "kPa" 
    rh_var.long_name = "the sea surface humidity observed by the waveglider "
    rh_var.units = "%" 
    true_wind_speed_var.long_name =  "the sea surface true wind speed observed by the waveglider"
    true_wind_speed_var.units = "m/s" 
    true_wind_dir_var.long_name = "the sea surface true wind direction observed by waveglider"
    true_wind_dir_var.units = "degree" 
    max_wind_speed_var.long_name = 'the sea surface max true wind speed observed by the waveglider'
    max_wind_speed_var.units = "m/s" 
    max_wind_dir_var.long_name = 'the sea surface true wind direction corresponding to maximum wind speed observed by the waveglider'
    max_wind_dir_var.units = "degree"
    seawater_temperature_var.long_name = 'seawater temperature of CTD observed by the waveglider'
    seawater_temperature_var.units = "Celsius"
    
    # 变量中写入数据
        # 必须time_var[:] = time_data，不可以time_var= time_data
        # 使用createVariable方法创建一个变量后，这个变量实际上是一个特殊的对象，它代表netCDF文件中的一个数据区域。
        # time_var = time_data会改变time_var的引用，而不是修改它所代表的数据区域的内容
        # 相反，time_var[:]是用来引用该变量整个数据区域的一个“切片”
        # time_var[:] = time_data 实际上是将time_data数组中的数据复制到time_var所代表的数据区域中
    time_var[:] = time
    lon_var[:] = lon
    lat_var[:] = lat
    ssat_var[:] = ssat
    ssap_var[:] = ssap
    rh_var[:] = rh
    true_wind_speed_var[:] = true_wind_speed
    true_wind_dir_var[:] = true_wind_dir
    max_wind_speed_var[:] = max_wind_speed
    max_wind_dir_var[:] = max_wind_dir
    seawater_temperature_var[:] = seawater_temperature

    # 全局属性(需要放到最后来，不然添加不上全局属性)
    file.WaveGlider_SN = AWG_Type + '_' + deviceID
    file.WaveGliderReleaseTime = ReleaseTime
    file.WaveGliderReleaseLongitude = ReleaseLongitude
    file.WaveGliderReleaseLatitude = ReleaseLatitude
    file.Sensor_accuracy = '海表气温，200WX-IPX7，±1.1℃；气压，200WX-IPX7，±1 hPa；湿度，200WX-IPX7，到最近的0.1%；风速，200WX-IPX7，0.1m/s；风向，200WX-IPX7，0.1°'
    file.Comment = Comment
    file.Information = information
    file.Manufacturer = '崂山实验室'
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