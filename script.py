import os
import overfitted_io_client as oc
from PIL import Image, ImageDraw, ImageFont



def draw_results(img_name, result):
    # render results on the image
    img = Image.open(img_name).convert('RGB')
    img_ext = Image.new('RGB', (img.size[0] + 500, img.size[1]), (0, 0, 0))
    img_ext.paste(img)
    draw = ImageDraw.Draw(img_ext, "RGB")
    

    color_index = 0
    text_offset = 20
    text_font = ImageFont.truetype("fonts/tahoma.ttf", 24)
    roi_index = 0

    for roi_name, roi_content in result['fields'].items():

        crt_color = COLORS_LIST[color_index]

        # draw rectangle
        draw.line([
                    (roi_content['coords']['p1'][0], roi_content['coords']['p1'][1]), 
                    (roi_content['coords']['p2'][0], roi_content['coords']['p2'][1]),
                    (roi_content['coords']['p3'][0], roi_content['coords']['p3'][1]),
                    (roi_content['coords']['p4'][0], roi_content['coords']['p4'][1]),
                    (roi_content['coords']['p1'][0], roi_content['coords']['p1'][1])
                ], fill=crt_color, width=5, joint='curve')

        # get current ROI name
        roi_name = ROU_ID_ROIS_ORDER[roi_index]

        # draw extracted text
        draw.text((img.size[0] + 20, text_offset), f"{roi_name}: ", font=text_font, fill=crt_color)
        draw.text((img.size[0] + 20 + 170, text_offset), f"'{roi_content['content']['text']}'", font=text_font, fill=(200, 200, 200))

        # draw line from rectangle to text
        draw.line([(roi_content['coords']['p2'][0], roi_content['coords']['p2'][1]), (img.size[0] + 10, text_offset + 15)], fill=crt_color, width = 3)  


        color_index = (color_index + 1) % len(COLORS_LIST)
        text_offset += 50
        roi_index += 1

    img_ext.save(f'outputs/{img_name}')



ROU_ID_ROIS = {
    'SERIES' : [583, 115, 632, 143],
    'NUMBER' : [669, 115, 791, 143], 
    'LAST_NAME' : [306, 194, 700, 229],
    'FIRST_NAME' : [306, 246, 700, 278],
    'NATIONALITY' : [306, 296, 600, 325],
    'ISSUED_BY' : [306, 490, 600, 522],
    'VALIDITY' : [670, 485, 1015, 530]
}

ROU_ID_ROIS_ORDER = ['SERIES', 'NUMBER', 'LAST_NAME', 'FIRST_NAME', 'NATIONALITY', 'ISSUED_BY', 'VALIDITY']

COLORS_LIST = [(255, 0, 100), (100, 255, 0), (0, 100, 255)]


# read image from disk
with open('target.png', 'rb') as img, open('template.jpg', 'rb') as template:


    # query the template parser
    response = oc.query_service(
        service = 'template-parser', 
        inputs = [
                    { 
                        'img' : img, 
                        'template_img' : template, 
                        'lang' : 'ro-ma', 
                        'api_key' : oc.config.get_api_key(), 
                        'rois' : ROU_ID_ROIS['SERIES'] + ROU_ID_ROIS['NUMBER'] + ROU_ID_ROIS['LAST_NAME'] + ROU_ID_ROIS['FIRST_NAME'] + ROU_ID_ROIS['NATIONALITY'] + ROU_ID_ROIS['ISSUED_BY'] + ROU_ID_ROIS['VALIDITY'],
                        'skip_seg' : 'true'
                    }
                ])

    result, status = response[0]
    draw_results(img_name = 'target.png', result = result)
    
    