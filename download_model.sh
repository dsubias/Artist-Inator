#!/bin/bash

if [ ! -d ./controlnet_model ]; then
  mkdir ./controlnet_model
fi
wget -O controlnet_model.zip "https://nas-graphics.unizar.es/s/8BiQBt98mGgKcGw/download/pretrained_models.zip" 
unzip controlnet_model.zip -d ./controlnet_model
