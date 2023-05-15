import subprocess

# 获取计算设备
temp = -1
while temp not in ['0', '11.7', '11.6', '11.2', '11.1', '10.2', '10.1']:
    temp = input(
        "输入你的计算设备\n CPU: 0\n GPU: 你的CUDA版本 可选([11.7, 11.6, 11.2, 11.1, 10.2, 10.1]) \n"
    )

# 安装部分依赖
command = 'pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple'
result = subprocess.run(command, shell=True)
print('\n', result)

# 安装paddlepaddle
paddlepaddle = {
    '0': 'python -m pip install paddlepaddle==2.3.2 -i https://pypi.tuna.tsinghua.edu.cn/simple',
    '11.7': 'python -m pip install paddlepaddle-gpu==2.3.2.post116 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html',
    '11.6': 'python -m pip install paddlepaddle-gpu==2.3.2.post116 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html',
    '11.2': 'python -m pip install paddlepaddle-gpu==2.3.2.post112 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html',
    '11.1': 'python -m pip install paddlepaddle-gpu==2.3.2.post111 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html',
    '10.2': 'python -m pip install paddlepaddle-gpu==2.3.2 -i https://pypi.tuna.tsinghua.edu.cn/simple',
    '10.1': 'python -m pip install paddlepaddle-gpu==2.3.2.post101 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html',
}
command = paddlepaddle[temp]
result = subprocess.run(command, shell=True)
print('\n', result)

torch = {
    '0': 'pip3 install torch torchvision torchaudio',
    '11.7': 'pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117',
    '11.6': 'pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116',
}

command = torch[temp]
result = subprocess.run(command, shell=True)
print('\n', result)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if result.returncode == 0:
    print(f"{bcolors.OKGREEN}{bcolors.BOLD} \nInstall Successfully {bcolors.ENDC}")
else:
    print(f"{bcolors.FAIL}{bcolors.BOLD} \n呜呜呜，没有装上，好可怜 {bcolors.ENDC}")
