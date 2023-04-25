FROM ubuntu:18.04

# 更换Ubuntu软件源为清华源，并安装所需的软件包，更换时区为Asia/Shanghai
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git nano wget ca-certificates curl tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 安装 Miniconda
ARG CONDA_PATH=/opt/miniconda
ENV PATH=$CONDA_PATH/bin:$PATH
RUN wget --quiet https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py37_23.1.0-1-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p $CONDA_PATH && \
    rm miniconda.sh && \
    conda config --set show_channel_urls yes && \
    conda install -y pip && \
    conda clean -ya && \
    conda init bash
COPY requirements /opt/project/
RUN pip install --no-cache-dir -r /opt/project/requirements
COPY tests /opt/project/
COPY scripts /opt/project/

WORKDIR /opt/project

CMD ["bash"]
