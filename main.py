import requests
import json
import time
import webcolors

def GET_request(url):
    """
    Sends a GET request to the specified URL and returns the 'LedColors' value from the response JSON object.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        list: The 'LedColors' value from the response JSON object, or None if the request failed.
    """
    # Send the GET request
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        print("GET request was successful!")
        #print("Response:", response.text)
        # the response is a JSON object
        # you can parse it using the json library
        json_object = json.loads(response.text)
        print(json_object)
        # get the layerid
        # layer_id = json_object[0]['LayerId']
        print("LedColors", json_object['LedColors'])

        return json_object['LedColors']
    else:
        print("GET request failed with status code:", response.status_code)
        return None

def GET_request_layer_id(url):
    # Send the GET request
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        print("GET request was successful!")
        print("Response:", response.text)
        # the response is a JSON object
        # you can parse it using the json library
        json_object = json.loads(response.text)
        print(json_object)
        # get the layerid
        layer_id = json_object[0]['LayerId']
        print("Layer ID:", layer_id)
        return layer_id
    else:
        print("GET request failed with status code:", response.status_code)
        return None

def POST_request(url, json_data):

    # Send the POST request with JSON data in the body
    response = requests.post(url, json=json_data)

    # Check the response
    if response.status_code == 200:
        #print("POST request was successful!")
        #print("Response:", response.text)
        return 1
    else:
        #print("POST request failed with status code:", response.status_code)
        return 0

def hex_to_rgb(hex_color):
    """Converts a hex color code to RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    """Converts an RGB color tuple to hex."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def interpolate_color(start_color, end_color, steps):
    """Interpolates between two colors."""
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    if steps == 1:
        return [rgb_to_hex(start_rgb)]
    delta_r = (end_rgb[0] - start_rgb[0]) / (steps - 1)
    delta_g = (end_rgb[1] - start_rgb[1]) / (steps - 1)
    delta_b = (end_rgb[2] - start_rgb[2]) / (steps - 1)
    colors = []
    for i in range(steps):
        r = int(start_rgb[0] + i * delta_r)
        g = int(start_rgb[1] + i * delta_g)
        b = int(start_rgb[2] + i * delta_b)
        colors.append(rgb_to_hex((r, g, b)))
    return colors

def change_color(url, interpolate_steps,colors,transition_time,time_repeated,leds):
    
    sleep_time = transition_time/interpolate_steps
    gradients = []
    for i,color in enumerate(colors):
        if i < (len(colors)-1):
            gradients.append(interpolate_color(colors[i], colors[i+1], interpolate_steps))
            print("Changing color to", i, colors[i],color)
    gradients.append(interpolate_color(colors[len(colors)-1],colors[0], interpolate_steps))
    
    for j in range(0, time_repeated):
        print("j:",j)
        gradient_colors = gradients[j%len(gradients)]
        for i in range(0, interpolate_steps):
            # print("Changing color to", i, gradient_colors[i])
            # Send the POST request with JSON data in the body
            color1 = gradient_colors[i]
            # will the next code modify leds?

            for led in leds:
                led['Color'] = color1
            try:
                color_name = webcolors.hex_to_name(led['Color'])
                
            except ValueError:
                color_name = led['Color']
            
            print(color_name)
            json_data = leds

            json_data_old = [
                {
                "LedId": "Mainboard1",
                "Color": color1
                },
                {
                "LedId": "Mainboard2",
                "Color": color1
                },
                {
                "LedId": "Mainboard3",
                "Color": color1
                },
                {
                "LedId": "Mainboard4",
                "Color": "#FFFFFF"
                },
                {
                "LedId": "Mainboard5",
                "Color": "#FFFFFF"
                }
            ]

            if POST_request(url, json_data):
                # wait for sleep_time ms
                
                time.sleep(sleep_time)
                continue

def main():
    layer_id = GET_request_layer_id(url = 'http://localhost:9696/remote-control-brushes')

    
    if layer_id is not None:
        print("Layer ID:", layer_id)
        url = 'http://localhost:9696/remote-control-brushes/' + layer_id + '/update-colors'
    else:
        print("Failed to get the layer ID.")
        return
    interpolate_steps = 50
    transition_time = 1
    time_repeated = 20
    

    url = 'http://localhost:9696/remote-control-brushes/' + layer_id
    print(url)
    result = GET_request(url)
    url = 'http://localhost:9696/remote-control-brushes/' + layer_id + '/update-colors'
    color_list = ['#ff00d5', '#F7FF00', '#11ff11']
    if result is not None:
        change_color(url, interpolate_steps,color_list,transition_time,time_repeated,result)     

if __name__ == '__main__':
    main()