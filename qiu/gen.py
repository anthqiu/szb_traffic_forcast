# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import sys
import math
import os
import shutil
import matplotlib.pyplot as plt
import requests
import osrm
import multiprocessing as mp


# %%
def GCJ2WGS(lon, lat):
    a = 6378245.0  # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323  # 克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324  # 圆周率
    # 以下为转换公式
    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + \
        0.1 * x * y + 0.1 * math.sqrt(abs(x))
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
             math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLon += (20.0 * math.sin(x * PI) + 40.0 *
             math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 *
             math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    # 纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * \
        y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
             math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLat += (20.0 * math.sin(y * PI) + 40.0 *
             math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 *
             math.sin(y * PI / 30.0)) * 2.0 / 3.0
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI)
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon, wgsLat


# %%
def map_matching(count, line, client):
    line = [x.strip().replace('"', '') for x in line.split(',', maxsplit=2)]
    traj = [x.strip() for x in line[2].split(',')]
    traj[0] = traj[0].replace('[', '')
    traj[-1] = traj[-1].replace(']', '')
    coordinates = []
    prop = []
    timestamps = []
    for t in traj:
        x = t.split(' ')
        time = int(x[-1])
        x, y, speed, direction = [float(xx) for xx in x[:4]]
        x, y = GCJ2WGS(x, y)
        coordinates.append([x, y])
        prop.append([time, speed, direction])
        timestamps.append(time)
    print(coordinates)
    response = client.match(coordinates=coordinates, overview=osrm.overview.full,
                            timestamps=timestamps, tidy=False, gaps=osrm.gaps.ignore)
    for r, p in zip(response['tracepoints'], prop):
        # if not r: continue
        # if r['name']=='': continue
        # if r['name'] not in out.keys():
        #     out[r['name']]=[]
        # out[r['name']].append(p)
        print(r, p)


# %%

def main():
    print("fuck!")
    src_file = sys.argv[1]
    start_line = int(sys.argv[2])
    end_line = int(sys.argv[3])
    client = osrm.Client(host='http://localhost:5000')
    with open(src_file, 'r') as src:
        cnt = -1
        pool = mp.Pool(8)
        manager = mp.Manager()
        p = []
        while True:
            line = src.readline()
            cnt += 1
            if cnt < start_line:
                continue
            if not line or cnt > end_line:
                break
            pp = pool.apply_async(map_matching, args=(cnt, line, client,))
            p.append(pp)
        pool.close()
        pool.join()


# %%

if __name__ == "__main__":
    main()
