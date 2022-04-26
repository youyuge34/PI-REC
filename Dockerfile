FROM pytorch/pytorch:1.0.1-cuda10.0-cudnn7-runtime

# Install things needed for easygui, tkinter and opencv
RUN apt-get update -y &&  \
    apt-get install -y build-essential libsm6 libxext6 libxrender-dev libxrender1 libfontconfig1 tk libglib2.0-0

RUN pip install --upgrade pip

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

#CMD ["python" "tool_draw.py" "-p" "models/getchu-anime" "-r"]
