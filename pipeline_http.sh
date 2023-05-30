echo "pipeline.sh <dataset_name> <open_world:cw/ow>"

# Parameter
result_path='/root/wfpdata/dataset_'$1'_'$2/
num_batch=20
urls_closeworld='input/urls-top-100.csv'
urls_openworld='input/urls-top-50000.csv'
tbbpath='/root/tor-browser'
torrc_dir_path=$PWD'/config/dataset_'$1'/torrc'
open_world_server_conf_path=$PWD'/config/dataset_'$1'/open_world_servers.csv'
open_world_num=10000
myexip='/root/myexip'

if [ $2 == 'ow' ]; then
    num_batch=1
fi

echo "result_path: "$result_path
echo "torrc_dir_path: " $torrc_dir_path
echo "num_batch: " $num_batch

# kill existing tor
pkill tor

# remove data
rm -rf ${result_path}

# Data collection
# conda activate py36
python data_collector.py --urls_closeworld ${urls_closeworld} --urls_openworld ${urls_openworld} --output ${result_path} --tbbpath ${tbbpath} --torrc_dir_path ${torrc_dir_path} --xvfb True --batch ${num_batch} --screenshot True --open_world $2 --open_world_num ${open_world_num} --open_world_server_conf_path ${open_world_server_conf_path} --myexip ${myexip} --http
