# 文件说明
- `data_processing.ipynb`：地图匹配脚本
- `gen.py`: Windows 下 multiprocessing 库无法在notebook中运行，可运行这一文件

# 搭建OSRM Docker镜像
- cd到OSRM文件夹
- 运行Docker命令：
    `docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/map.osrm --max-matching-size=10000`
    即可。