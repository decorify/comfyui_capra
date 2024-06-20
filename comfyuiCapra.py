import gradio as gr
import json
#from urllib import request, parse
import requests
import time
import random
from PIL import Image
import io

global comfyurl

import requests
import json

def queue_prompt(prompt):
    payload = {"prompt": prompt}
    response = requests.post(comfyurl + "/prompt", json=payload)
    response.raise_for_status()
    content_json = response.json()
    print(content_json)
    return content_json['prompt_id']
def history(prompt_id,outindex):    
    while True:
        try:
            response = requests.get(comfyurl + "/history/" + prompt_id)
            response.raise_for_status()  # 检查请求是否成功
            content_json = response.json()
            print(content_json)
            if len(content_json) != 0:
                break
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP错误: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"连接错误: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"超时错误: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"其他错误: {err}")

    filenames = []
    if prompt_id in content_json and 'outputs' in content_json[prompt_id] and outindex in content_json[prompt_id]['outputs']:
        for output_type in content_json[prompt_id]['outputs'][outindex]:
            for item in content_json[prompt_id]['outputs'][outindex][output_type]:
                filenames.append(item['filename'])

    print(filenames[0])
    return filenames[0]
def uploadImage(image_data, image_upload_type, overwrite=False, subfolder=""):
    """
    使用 requests 同步发送图像文件到服务器。
    """
    url = comfyurl + "/upload/image"
    # 将图像数据转换为一个文件对象
    image_file = io.BytesIO()
    image = Image.fromarray(image_data)
    image.save(image_file, format='PNG')
    image_file.seek(0)
    image_file.name = 'huimie' + str(random.randint(1000, 9999)) + '.png'  # 使用randint生成随机整数并转换为字符串

    # 构建请求的数据
    files = {'image': image_file}
    data = {
        'type': image_upload_type,
        'overwrite': 'true' if overwrite else 'false',
        'subfolder': subfolder
    }

    # 发送 POST 请求
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        # 请求成功
        return response.json()
    else:
        # 请求失败
        print("请求失败，状态码：", response.status_code)
        return None

# 定义处理文件的函数
def read_file_content(file_obj):
    # 使用 with 语句确保文件正确关闭
    with open(file_obj.name, "r", encoding="utf-8") as file:
        content = file.read()  # 读取文件内容
    return content
def process_inputs(comfyui_address, api_file, image, input1,input2,input3,input4,input5,input6,input7,input8,input9):
    global comfyurl
    if comfyui_address.endswith('/'):
        comfyui_address = comfyui_address[:-1]
    comfyurl=comfyui_address
    prompt_workflow= json.loads(read_file_content(api_file))
    
    load_image_key=None
    # 遍历JSON对象，查找class_type为'LoadImage'的节点
    for key, value in prompt_workflow.items():
        if value.get('class_type') == 'LoadImage':
            load_image_key = key
        if 'seed' in value.get('inputs', {}):
            seed_node_key = key
            prompt_workflow[seed_node_key]["inputs"]["seed"] = random.randint(1, 18446744073709551614) 
        if value.get('_meta', {}).get('title') == 'input1':
            input1 = key
            prompt_workflow[input1]["inputs"]["text"]=input1
        if value.get('_meta', {}).get('title') == 'input2':
            input2 = key
            prompt_workflow[input2]["inputs"]["text"]=input2
        if value.get('_meta', {}).get('title') == 'input3':
            input3 = key
            prompt_workflow[input3]["inputs"]["text"]=input3
        if value.get('_meta', {}).get('title') == 'input4':
            input4 = key
            prompt_workflow[input4]["inputs"]["text"]=input4
        if value.get('_meta', {}).get('title') == 'input5':
            input5 = key
            prompt_workflow[input5]["inputs"]["text"]=input5
        if value.get('_meta', {}).get('title') == 'input6':
            input6 = key
            prompt_workflow[input6]["inputs"]["text"]=input6
        if value.get('_meta', {}).get('title') == 'input7':
            input7 = key
            prompt_workflow[input7]["inputs"]["text"]=input7
        if value.get('_meta', {}).get('title') == 'input8':
            input8 = key
            prompt_workflow[input8]["inputs"]["text"]=input8
        if value.get('_meta', {}).get('title') == 'input9':
            input9 = key
            prompt_workflow[input9]["inputs"]["text"]=input9
            
        if value.get('class_type') == 'SaveImage':
            save_image_key = key
        if value.get('_meta', {}).get('title') == 'output':
            save_image_key = key
            

    if(image is not None):
        res=uploadImage(image,None)
        filename=res.get('name')
        print(filename)
        if load_image_key is not None:
            print(f"LoadImage节点的序列号是: {load_image_key}")
            prompt_workflow[load_image_key]["inputs"]["image"]=filename
        else:
            print("没有找到LoadImage节点")
 
    promptid=queue_prompt(prompt_workflow)
    print(save_image_key)
    filename2=history(promptid,save_image_key)
    print(comfyurl+"/view?filename="+filename2)
    return comfyurl+"/view?filename="+filename2,gr.update(visible=True)
def update_ui(api_file):
   
    prompt_workflow= json.loads(read_file_content(api_file))
    
    load_image_key = None
    input1 = None
    input2 = None
    input3 = None
    input4 = None
    input5 = None
    input6 = None
    input7 = None
    input8 = None
    input9 = None
    # 遍历JSON对象，查找class_type为'LoadImage'的节点
    for key, value in prompt_workflow.items():
        if value.get('class_type') == 'LoadImage':
            load_image_key = key
        if value.get('_meta', {}).get('title') == 'input1':
            input1 = key
        if value.get('_meta', {}).get('title') == 'input2':
            input2 = key
        if value.get('_meta', {}).get('title') == 'input3':
            input3 = key
        if value.get('_meta', {}).get('title') == 'input4':
            input4 = key
        if value.get('_meta', {}).get('title') == 'input5':
            input5 = key
        if value.get('_meta', {}).get('title') == 'input6':
            input6 = key
        if value.get('_meta', {}).get('title') == 'input7':
            input7 = key
        if value.get('_meta', {}).get('title') == 'input8':
            input8 = key
        if value.get('_meta', {}).get('title') == 'input9':
            input9 = key
    
    return [gr.update(visible=load_image_key!=None),gr.update(visible=input1!=None),gr.update(visible=input2!=None),gr.update(visible=input3!=None),gr.update(visible=input4!=None),gr.update(visible=input5!=None),gr.update(visible=input6!=None),gr.update(visible=input7!=None),gr.update(visible=input8!=None),gr.update(visible=input9!=None),gr.update(visible=True),gr.update(visible=True)]
def sharework(comfyui_address, api_file, image, input1,input2,input3,input4,input5,input6,input7,input8,input9,output_image):
    print(output_image)
    
with gr.Blocks() as demo:
    gr.Markdown("# Capra")
    gr.Markdown("简洁至上，直达核心")
    with gr.Accordion("系统配置"):
        with gr.Row():
            with gr.Column():
                comfyui_address = gr.Textbox(label="请输入comfyui地址", value="http://127.0.0.1:8188")
                api_file = gr.File(label="请选择工作流api文件")
                submit_button0 = gr.Button("确认配置")   
    image = gr.Image(label="如果有LoadImage节点，请上传图片",width=500 , visible=False)
    input1 = gr.Textbox(label="请输入（对应节点命名input1）", visible=False)
    input2 = gr.Textbox(label="请输入（对应节点命名input2）", visible=False)
    input3 = gr.Textbox(label="请输入（对应节点命名input3）", visible=False)
    input4 = gr.Textbox(label="请输入（对应节点命名input4）", visible=False)
    input5 = gr.Textbox(label="请输入（对应节点命名input5）", visible=False)
    input6 = gr.Textbox(label="请输入（对应节点命名input6）", visible=False)
    input7 = gr.Textbox(label="请输入（对应节点命名input7）", visible=False)
    input8 = gr.Textbox(label="请输入（对应节点命名input8）", visible=False)
    input9 = gr.Textbox(label="请输入（对应节点命名input9）", visible=False)
    submit_button = gr.Button("提交", visible=False)
    
 
    output_image = gr.Image(label="输出",width=500 ,visible=False)  # 图片输出
    publish_button = gr.Button("分享（开源版本不支持）", visible=False)
    
    # 定义一个按钮来触发处理函数
    

    # 当按钮被点击时，调用process_inputs函数，并将结果显示在output_image中
    submit_button0.click(
            fn=update_ui,
            inputs=api_file,
            outputs=[image,input1,input2,input3,input4,input5,input6,input7,input8,input9,submit_button,output_image]
    )
    submit_button.click(
        fn=process_inputs,
        inputs=[comfyui_address, api_file, image, input1,input2,input3,input4,input5,input6,input7,input8,input9],
        outputs=[output_image,publish_button]
    )
    publish_button.click(
        fn=sharework,
        inputs=[comfyui_address, api_file, image, input1,input2,input3,input4,input5,input6,input7,input8,input9,output_image],
        #outputs=[output_image,publish_button]
    )

demo.launch(server_name="127.0.0.1")